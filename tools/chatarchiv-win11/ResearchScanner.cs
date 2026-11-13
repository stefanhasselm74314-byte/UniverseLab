using System.Text;
using System.Text.RegularExpressions;

namespace UniverseLab.ChatArchiv.Win11;

public sealed record ResearchFinding(string ChatId, string ChatTitle, int Number, string Role,
    string Kind, string Signal, string Excerpt, int Priority);

/// <summary>
/// A bounded, explicitly heuristic review of old wording. No source/canon validation.
/// </summary>
public static class ResearchScanner
{
    private static readonly Regex Blocked = new(@"(?i)\b(BLOCKIERT|NOT[_ -]?(RELEASED|ADMISSIBLE|READY))\b|\bBLOCKER\s*[:=]\s*\S.{10,}", RegexOptions.Compiled);
    private static readonly Regex Conflict = new(@"(?i)\[\s*(WIDERSPRUCH|KONFLIKT|INKONSISTENZ)\s*\]|\b(WIDERSPRUCH|KONFLIKT|INKONSISTENZ)\s*[:=]", RegexOptions.Compiled);
    private static readonly Regex Open = new(@"(?i)\[\s*OFFEN\s*\]|\bUNGEKLÄRT\b|\bPENDING\b|\b(NICHT\s+(NACHGEWIESEN|VALIDIERT|BELEGT)|BLEIBT\s+OFFEN|NOCH\s+OFFEN)\b|\bOFFEN\s*[:=]", RegexOptions.Compiled);
    private static readonly Regex Next = new(@"(?i)\b(NÄCHSTER\s+SCHRITT|NEXT\s+STEP|TODO)\s*[:=]|\bNOCH\s+ZU\s+PRÜFEN\b", RegexOptions.Compiled);
    private static readonly Regex Negation = new(@"(?i)\b(KEINE?\s+(AKTUELLEN?\s+)?(BLOCKER|WIDERSPRÜCHE?|KONFLIKTE?)|NICHT\s+BLOCKIERT|WIDERSPRUCHSFREI|BLOCKER\s*[:=]\s*(KEINE?|NEIN|0|N/A))\b", RegexOptions.Compiled);
    private static readonly Regex Placeholder = new(@"(?i)^\s*(\d+(\.\d+)*\s*)?(NOCH\s+)?OFFEN(\s*[/|\-–]\s*(SPÄTERER?\s+)?AUSBAU)?\s*[.!?:]?\s*$", RegexOptions.Compiled);

    public static List<ResearchFinding> Scan(ArchiveStore store, IEnumerable<ArchiveEntry> entries,
        Action<int, int>? progress = null, CancellationToken cancellation = default)
    {
        var source = entries.ToList();
        var result = new List<ResearchFinding>();
        for (int chatIndex = 0; chatIndex < source.Count; chatIndex++)
        {
            cancellation.ThrowIfCancellationRequested();
            var chat = source[chatIndex];
            List<VisibleMessage> messages;
            try { messages = store.Messages(chat); }
            catch (Exception) { continue; }
            var chatFindings = new List<ResearchFinding>();
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            for (int i = messages.Count - 1; i >= Math.Max(0, messages.Count - 350); i--)
            {
                string body = messages[i].Body;
                if (body.Length > 120000) body = body[^120000..];
                int perMessage = 0;
                foreach (string line in body.Split('\n'))
                {
                    string cleaned = line.Trim().TrimStart('#', '*', '|', '>', '-', ' ', '\t');
                    if (cleaned.Length < 18 || Placeholder.IsMatch(cleaned) || Negation.IsMatch(cleaned)) continue;
                    Match match;
                    string kind;
                    int priority;
                    if ((match = Blocked.Match(cleaned)).Success) { kind = "Blocker"; priority = 100; }
                    else if ((match = Conflict.Match(cleaned)).Success) { kind = "Konflikt"; priority = 90; }
                    else if ((match = Open.Match(cleaned)).Success) { kind = "Offener Punkt"; priority = 70; }
                    else if ((match = Next.Match(cleaned)).Success) { kind = "Nächster Schritt"; priority = 50; }
                    else continue;
                    string marker = match.Value;
                    if (!seen.Add(marker + "|" + cleaned)) continue;
                    int start = Math.Max(0, match.Index - 120);
                    int length = Math.Min(cleaned.Length - start, 420);
                    string excerpt = (start > 0 ? "…" : "") + cleaned.Substring(start, length) +
                        (start + length < cleaned.Length ? "…" : "");
                    chatFindings.Add(new ResearchFinding(chat.Id, chat.Title, i + 1, messages[i].Role,
                        kind, marker, excerpt, priority));
                    if (++perMessage == 2) break;
                }
            }
            result.AddRange(chatFindings.OrderByDescending(f => f.Priority).ThenByDescending(f => f.Number).Take(5));
            if (chatIndex % 5 == 0) progress?.Invoke(chatIndex + 1, source.Count);
        }
        return result.OrderByDescending(f => f.Priority).ThenBy(f => f.ChatTitle).ToList();
    }

    public static string Handoff(IEnumerable<ResearchFinding> findings)
    {
        var chosen = findings.Take(12).ToList();
        var sb = new StringBuilder();
        sb.AppendLine("# UniverseLab – Chat-Übergabe (lokale Fundstellen)")
            .AppendLine().AppendLine("[HEURISTISCH] Die folgenden Zitate sind historische Suchtreffer, keine bestätigten heutigen Forschungslücken.")
            .AppendLine("Jede Aussage anhand des Originalchats und des aktuellen Projektkanons prüfen; keine automatische Freigabe.")
            .AppendLine();
        for (int i = 0; i < chosen.Count; i++)
        {
            var finding = chosen[i];
            sb.AppendLine($"## {i + 1}. {finding.Kind} – {finding.ChatTitle}")
                .AppendLine($"- Chat-ID: `{finding.ChatId}`")
                .AppendLine($"- Sichtbarer Beitrag: {finding.Number} ({finding.Role})")
                .AppendLine($"- Auslöser: `{finding.Signal}`")
                .AppendLine($"- Quellausschnitt: {finding.Excerpt}")
                .AppendLine("- Prüffrage: Ist der Punkt im aktuellen Projektstand noch offen, und was belegt die Antwort?")
                .AppendLine();
        }
        sb.AppendLine("Arbeitsauftrag: Prüfe Originalkontext, Datum, späteren Verlauf und aktuelle kanonische Quellen.")
            .AppendLine("Trenne [BEWIESEN], [NUMERISCH BESTÄTIGT], [KONDITIONAL], [HEURISTISCH], [OFFEN], [BLOCKIERT].")
            .AppendLine("Technische Ausführbarkeit ist weder physikalische Identifikation noch empirische Bestätigung.");
        return sb.ToString();
    }
}
