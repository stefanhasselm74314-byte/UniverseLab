using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace UniverseLab.ChatArchiv.Win11;

public sealed class ArchiveEntry
{
    public string Id { get; set; } = "";
    public string Title { get; set; } = "Ohne Titel";
    public string File { get; set; } = "";
    public double Created { get; set; }
    public string Category { get; set; } = "andere";
    public string Digest { get; set; } = "";
    public double Updated { get; set; }
    public int NodeCount { get; set; }
    public string Date => Created > 0 && Created < 253402300799
        ? DateTimeOffset.FromUnixTimeSeconds((long)Created).ToLocalTime().ToString("dd.MM.yyyy")
        : "Unbekannt";
}

public sealed record VisibleMessage(string Role, string Body, double Created);

public sealed class ImportCounts
{
    public int Added { get; set; }
    public int Updated { get; set; }
    public int Unchanged { get; set; }
    public int Older { get; set; }
    public int Errors { get; set; }
    public override string ToString() =>
        $"Neu: {Added}  ·  Aktualisiert: {Updated}  ·  Identisch: {Unchanged}  ·  Ältere Fassungen: {Older}  ·  Fehler: {Errors}";
}

/// <summary>
/// Offline archive. Does not access the Internet, the ChatGPT client, or Android app data.
/// The original JSON mapping is kept, including alternative response branches.
/// </summary>
public sealed class ArchiveStore
{
    private const long MaxConversationJsonBytes = 3L * 1024 * 1024 * 1024;
    private readonly string _root;
    private readonly string _conversations;
    private readonly string _versions;
    private readonly string _indexFile;
    private readonly Dictionary<string, ArchiveEntry> _entries = new(StringComparer.Ordinal);
    private readonly JsonSerializerOptions _jsonOptions = new() { WriteIndented = false, MaxDepth = 128 };

    public ArchiveStore(string? root = null)
    {
        _root = root ?? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "UniverseLab", "ChatArchiv-Win11");
        _conversations = Path.Combine(_root, "conversations");
        _versions = Path.Combine(_root, "conversation-versions");
        _indexFile = Path.Combine(_root, "index.json");
        Directory.CreateDirectory(_conversations);
        Directory.CreateDirectory(_versions);
        if (!File.Exists(_indexFile)) return;
        var records = JsonSerializer.Deserialize<List<ArchiveEntry>>(File.ReadAllText(_indexFile)) ?? [];
        foreach (var entry in records)
        {
            if (entry.Id.Length == 0 || !System.Text.RegularExpressions.Regex.IsMatch(entry.File, "^[0-9a-f]{64}\\.json$"))
                continue;
            _entries[entry.Id] = entry;
        }
    }

    public List<ArchiveEntry> Snapshot() => _entries.Values
        .OrderByDescending(entry => entry.Created).ThenBy(entry => entry.Title).ToList();

    public int Count => _entries.Count;

    public static bool IsConversationJson(string name) => name.StartsWith("conversations", StringComparison.OrdinalIgnoreCase)
        && name.EndsWith(".json", StringComparison.OrdinalIgnoreCase);

    public async Task<ImportCounts> ImportAsync(IEnumerable<string> filenames, Action<ImportCounts>? progress = null,
        CancellationToken cancellation = default)
    {
        var result = new ImportCounts();
        foreach (string filename in filenames)
        {
            cancellation.ThrowIfCancellationRequested();
            try
            {
                if (filename.EndsWith(".zip", StringComparison.OrdinalIgnoreCase))
                    await ImportZipAsync(filename, result, progress, cancellation);
                else if (IsConversationJson(Path.GetFileName(filename)))
                {
                    await using var stream = File.OpenRead(filename);
                    await ImportJsonAsync(stream, result, progress, cancellation);
                }
                else throw new InvalidDataException("Erwartet: conversations*.json oder ZIP");
                SaveIndex();
            }
            catch (OperationCanceledException) { SaveIndex(); throw; }
            catch (Exception exception)
            {
                result.Errors++;
                progress?.Invoke(result);
                throw new IOException($"{Path.GetFileName(filename)}: {exception.Message}", exception);
            }
        }
        SaveIndex();
        return result;
    }

    private async Task ImportZipAsync(string filename, ImportCounts result, Action<ImportCounts>? progress,
        CancellationToken cancellation)
    {
        var previouslyKnownIds = new HashSet<string>(_entries.Keys, StringComparer.Ordinal);
        using var zip = ZipFile.OpenRead(filename);
        var candidates = zip.Entries.Where(entry => !string.IsNullOrEmpty(entry.Name) && IsConversationJson(entry.Name)).ToList();
        if (candidates.Count == 0) throw new InvalidDataException("Kein conversations*.json im ZIP");
        if (candidates.Count > 100) throw new InvalidDataException("Mehr als 100 Gesprächs-JSONs im ZIP");
        long consumed = 0;
        foreach (var item in candidates)
        {
            cancellation.ThrowIfCancellationRequested();
            if (item.Length > MaxConversationJsonBytes - consumed)
                throw new InvalidDataException("ZIP enthält über 3 GiB Gesprächs-JSON");
            await using var stream = item.Open();
            await using var limited = new LimitedStream(stream, MaxConversationJsonBytes - consumed);
            await ImportJsonAsync(limited, result, progress, cancellation);
            consumed += limited.ReadCount;
        }

        var manifest = zip.Entries.FirstOrDefault(entry => entry.FullName == "chatarchiv_manifest.json");
        if (manifest != null && manifest.Length <= 2 * 1024 * 1024)
        {
            using var input = manifest.Open();
            using var doc = await JsonDocument.ParseAsync(input, cancellationToken: cancellation);
            if (doc.RootElement.GetPropertyOrDefault("format").GetStringOrNull() == "universelab-chatarchiv")
            {
                var categories = doc.RootElement.GetPropertyOrDefault("category_by_id");
                if (categories.ValueKind == JsonValueKind.Object)
                    foreach (var pair in categories.EnumerateObject())
                        if (!previouslyKnownIds.Contains(pair.Name) &&
                            _entries.TryGetValue(pair.Name, out var entry) &&
                            pair.Value.GetStringOrNull() is "projekt" or "andere")
                            entry.Category = pair.Value.GetString()!;
            }
        }
    }

    private async Task ImportJsonAsync(Stream source, ImportCounts result, Action<ImportCounts>? progress,
        CancellationToken cancellation)
    {
        await foreach (var item in JsonSerializer.DeserializeAsyncEnumerable<JsonElement>(source, _jsonOptions,
            cancellationToken: cancellation))
        {
            cancellation.ThrowIfCancellationRequested();
            if (item.ValueKind != JsonValueKind.Object) continue;
            string id = item.GetPropertyOrDefault("id").GetStringOrNull() ?? "";
            if (id.Length == 0 || item.GetPropertyOrDefault("mapping").ValueKind != JsonValueKind.Object) continue;
            string raw = item.GetRawText();
            string digest = Sha(raw);
            var previous = _entries.GetValueOrDefault(id);
            if (previous?.Digest == digest) { result.Unchanged++; continue; }

            var mapping = item.GetProperty("mapping");
            double updated = item.GetPropertyOrDefault("update_time").GetNumberOrZero();
            int nodeCount = mapping.EnumerateObject().Count();
            if (previous != null && (updated < previous.Updated ||
                (updated == previous.Updated && nodeCount <= previous.NodeCount)))
            {
                SaveVersion(id, digest, raw);
                result.Older++;
                continue;
            }

            string file = Sha(id) + ".json";
            string destination = Path.Combine(_conversations, file);
            if (previous != null && File.Exists(destination))
                SaveVersion(id, previous.Digest, File.ReadAllText(destination));
            AtomicWrite(destination, raw);
            string title = item.GetPropertyOrDefault("title").GetStringOrNull() ?? "Ohne Titel";
            if (string.IsNullOrWhiteSpace(title)) title = "Ohne Titel";
            AtomicWrite(Path.Combine(_conversations, Sha(id) + ".search"),
                string.Join("\n", VisibleConversation.Extract(item).Select(message => message.Body)).ToLowerInvariant());
            _entries[id] = new ArchiveEntry
            {
                Id = id, Title = title, File = file,
                Created = item.GetPropertyOrDefault("create_time").GetNumberOrZero(),
                Updated = updated, NodeCount = nodeCount, Digest = digest,
                Category = previous?.Category ?? ClassifyTitle(title)
            };
            if (previous == null) result.Added++; else result.Updated++;
            if ((result.Added + result.Updated) % 10 == 0)
            {
                SaveIndex();
                progress?.Invoke(result);
            }
        }
    }

    public static string ClassifyTitle(string title)
    {
        string input = title.ToLowerInvariant();
        return new[] { "universelab", "hyperzeit", "hzt", "hpvs", "mond", "brane", "baryogenese" }
            .Any(input.Contains) ? "projekt" : "andere";
    }

    public void SetCategory(string id, string category)
    {
        if (!_entries.TryGetValue(id, out var item) || category is not ("projekt" or "andere")) return;
        item.Category = category;
        SaveIndex();
    }

    public List<VisibleMessage> Messages(ArchiveEntry item)
    {
        using var doc = JsonDocument.Parse(File.ReadAllText(Path.Combine(_conversations, item.File)));
        return VisibleConversation.Extract(doc.RootElement);
    }

    public string OriginalJson(ArchiveEntry item) => File.ReadAllText(Path.Combine(_conversations, item.File));

    public static string Markdown(ArchiveEntry item, IReadOnlyList<VisibleMessage> messages)
    {
        var sb = new StringBuilder();
        sb.AppendLine("# " + item.Title).AppendLine().AppendLine("Chat-ID: " + item.Id).AppendLine();
        for (int index = 0; index < messages.Count; index++)
        {
            sb.AppendLine($"## {index + 1}. {(messages[index].Role == "user" ? "Stefan" : "Assistant")}")
                .AppendLine().AppendLine(messages[index].Body).AppendLine();
        }
        return sb.ToString();
    }

    public async Task<List<ArchiveEntry>> SearchAsync(IEnumerable<ArchiveEntry> entries, string query,
        CancellationToken cancellation)
    {
        query = query.Trim().ToLowerInvariant();
        if (query.Length == 0) return entries.ToList();
        var matches = new List<ArchiveEntry>();
        foreach (var entry in entries)
        {
            cancellation.ThrowIfCancellationRequested();
            if (entry.Title.Contains(query, StringComparison.OrdinalIgnoreCase)) { matches.Add(entry); continue; }
            string file = Path.Combine(_conversations, Sha(entry.Id) + ".search");
            if (!File.Exists(file)) continue;
            // Stream the search index instead of loading every chat into the UI at once.
            using var reader = File.OpenText(file);
            var overlap = "";
            var buffer = new char[16384];
            int count;
            while ((count = await reader.ReadAsync(buffer, cancellation)) != 0)
            {
                var part = overlap + new string(buffer, 0, count).ToLowerInvariant();
                if (part.Contains(query, StringComparison.Ordinal)) { matches.Add(entry); break; }
                overlap = part[^Math.Min(part.Length, query.Length + 8)..];
            }
        }
        return matches;
    }

    public async Task BackupAsync(string filename, Action<int, int>? progress, CancellationToken cancellation)
    {
        var entries = Snapshot();
        using var zip = ZipFile.Open(filename, ZipArchiveMode.Create);
        var conversations = zip.CreateEntry("conversations-000.json", CompressionLevel.Fastest);
        await using (var stream = conversations.Open())
        {
            byte[] comma = [(byte)','];
            await stream.WriteAsync(new byte[] { (byte)'[' }, cancellation);
            for (int i = 0; i < entries.Count; i++)
            {
                cancellation.ThrowIfCancellationRequested();
                if (i > 0) await stream.WriteAsync(comma, cancellation);
                await using var input = File.OpenRead(Path.Combine(_conversations, entries[i].File));
                await input.CopyToAsync(stream, cancellation);
                progress?.Invoke(i + 1, entries.Count);
            }
            await stream.WriteAsync(new byte[] { (byte)']' }, cancellation);
        }
        var manifest = zip.CreateEntry("chatarchiv_manifest.json");
        await using (var output = manifest.Open())
        {
            await JsonSerializer.SerializeAsync(output, new
            {
                format = "universelab-chatarchiv", version = 1, conversation_count = entries.Count,
                category_by_id = entries.ToDictionary(e => e.Id, e => e.Category)
            }, cancellationToken: cancellation);
        }
    }

    private void SaveIndex() => AtomicWrite(_indexFile, JsonSerializer.Serialize(_entries.Values.ToList()));

    private void SaveVersion(string id, string digest, string data)
    {
        string path = Path.Combine(_versions, Sha(id) + "-" + digest + ".json");
        if (File.Exists(path)) return;
        if (Directory.EnumerateFiles(_versions).Sum(file => new FileInfo(file).Length) + Encoding.UTF8.GetByteCount(data) > 1024L * 1024 * 1024)
            throw new IOException("1-GiB-Limit für ältere Chatversionen erreicht");
        AtomicWrite(path, data);
    }

    private static string Sha(string value) => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();

    private static void AtomicWrite(string path, string data)
    {
        string temp = path + ".tmp";
        File.WriteAllText(temp, data, new UTF8Encoding(false));
        File.Move(temp, path, true);
    }

    private sealed class LimitedStream : Stream
    {
        private readonly Stream _input;
        private readonly long _limit;
        public long ReadCount { get; private set; }
        public LimitedStream(Stream input, long limit) { _input = input; _limit = limit; }
        public override int Read(byte[] buffer, int offset, int count)
        {
            int value = _input.Read(buffer, offset, (int)Math.Min(count, _limit - ReadCount + 1));
            ReadCount += value;
            if (ReadCount > _limit) throw new InvalidDataException("ZIP-Entpacklimit überschritten");
            return value;
        }
        public override ValueTask<int> ReadAsync(Memory<byte> buffer, CancellationToken cancellationToken = default)
            => ReadLimitedAsync(buffer, cancellationToken);
        private async ValueTask<int> ReadLimitedAsync(Memory<byte> buffer, CancellationToken cancellationToken)
        {
            int value = await _input.ReadAsync(buffer[..(int)Math.Min(buffer.Length, _limit - ReadCount + 1)], cancellationToken);
            ReadCount += value;
            if (ReadCount > _limit) throw new InvalidDataException("ZIP-Entpacklimit überschritten");
            return value;
        }
        public override bool CanRead => true;
        public override bool CanSeek => false;
        public override bool CanWrite => false;
        public override long Length => throw new NotSupportedException();
        public override long Position { get => ReadCount; set => throw new NotSupportedException(); }
        public override void Flush() { }
        public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
        public override void SetLength(long value) => throw new NotSupportedException();
        public override void Write(byte[] buffer, int offset, int count) => throw new NotSupportedException();
    }
}

public static class JsonExtensions
{
    public static JsonElement GetPropertyOrDefault(this JsonElement element, string name) =>
        element.ValueKind == JsonValueKind.Object && element.TryGetProperty(name, out var value) ? value : default;

    public static string? GetStringOrNull(this JsonElement element) =>
        element.ValueKind == JsonValueKind.String ? element.GetString() : null;

    public static double GetNumberOrZero(this JsonElement element) =>
        element.ValueKind == JsonValueKind.Number && element.TryGetDouble(out var value) && double.IsFinite(value)
            ? value : 0;
}

public static class VisibleConversation
{
    public static List<VisibleMessage> Extract(JsonElement root)
    {
        var result = new List<VisibleMessage>();
        JsonElement mapping = root.GetPropertyOrDefault("mapping");
        if (mapping.ValueKind != JsonValueKind.Object) return result;
        string nodeId = root.GetPropertyOrDefault("current_node").GetStringOrNull() ?? "";
        var seen = new HashSet<string>(StringComparer.Ordinal);
        while (nodeId.Length > 0 && seen.Add(nodeId) && seen.Count < 100000 &&
               mapping.TryGetProperty(nodeId, out var node))
        {
            var message = ParseNode(node);
            if (message != null) result.Add(message);
            nodeId = node.GetPropertyOrDefault("parent").GetStringOrNull() ?? "";
        }
        result.Reverse();
        return result;
    }

    private static VisibleMessage? ParseNode(JsonElement node)
    {
        var message = node.GetPropertyOrDefault("message");
        if (message.ValueKind != JsonValueKind.Object) return null;
        var role = message.GetPropertyOrDefault("author").GetPropertyOrDefault("role").GetStringOrNull() ?? "";
        if (role is not ("user" or "assistant")) return null;
        var metadata = message.GetPropertyOrDefault("metadata");
        if (metadata.GetPropertyOrDefault("is_visually_hidden_from_conversation").ValueKind == JsonValueKind.True)
            return null;
        if (metadata.GetPropertyOrDefault("channel").GetStringOrNull() is "analysis" or "justify" or "confidence" or "summary")
            return null;
        if (role == "assistant" && message.GetPropertyOrDefault("recipient").GetStringOrNull() is string target
            && target is not ("all" or "")) return null;
        var content = message.GetPropertyOrDefault("content");
        if (content.GetPropertyOrDefault("content_type").GetStringOrNull() is not ("text" or "multimodal_text"))
            return null;
        var parts = content.GetPropertyOrDefault("parts");
        if (parts.ValueKind != JsonValueKind.Array) return null;
        var lines = new List<string>();
        bool attachment = false;
        foreach (var part in parts.EnumerateArray())
        {
            if (part.ValueKind == JsonValueKind.String) lines.Add(part.GetString() ?? "");
            else if (part.ValueKind == JsonValueKind.Object)
            {
                var text = part.GetPropertyOrDefault("text").GetStringOrNull();
                if (!string.IsNullOrEmpty(text)) lines.Add(text);
                else attachment = true;
            }
        }
        var visible = string.Join("\n", lines).Trim();
        if (attachment) visible += "\n\n[Medienanhang: zusätzliche Exportdatei erforderlich]";
        if (string.IsNullOrWhiteSpace(visible)) return null;
        return new VisibleMessage(role, visible, message.GetPropertyOrDefault("create_time").GetNumberOrZero());
    }
}
