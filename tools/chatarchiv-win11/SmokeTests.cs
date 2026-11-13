using System.IO.Compression;
using System.Text.Json;

namespace UniverseLab.ChatArchiv.Win11;

internal static class SmokeTests
{
    public static int Run()
    {
        var root = Path.Combine(Path.GetTempPath(), "UniverseLab-Win11-Smoke-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            Execute(root).GetAwaiter().GetResult();
            Console.WriteLine("PASS: import, duplicate, active branch, hidden assistant content, search, handoff, backup");
            return 0;
        }
        catch (Exception exception)
        {
            Console.Error.WriteLine("FAIL: " + exception);
            return 1;
        }
        finally { Directory.Delete(root, recursive: true); }
    }

    private static async Task Execute(string root)
    {
        string export = Path.Combine(root, "conversations-000.json");
        const string json = """
            [
              {"id":"chat-123","title":"UniverseLab Test","create_time":1711111111,"update_time":1711112222,
                "current_node":"hidden","mapping":{
                  "first":{"parent":null,"message":{"author":{"role":"user"},
                    "content":{"content_type":"text","parts":["Bitte prüfe den Blocker: Not released, nächster Schritt ist der dimensionslose Rangtest."]}}},
                  "second":{"parent":"first","message":{"author":{"role":"assistant"},"recipient":"all",
                    "content":{"content_type":"text","parts":["[OFFEN] Die Nullmode ist noch nicht validiert."]}}},
                  "hidden":{"parent":"second","message":{"author":{"role":"assistant"},
                    "metadata":{"channel":"analysis"},"content":{"content_type":"text","parts":["Nicht sichtbare interne Notiz"]}}}
                }
              }
            ]
            """;
        await File.WriteAllTextAsync(export, json);
        var store = new ArchiveStore(Path.Combine(root, "private"));
        var first = await store.ImportAsync([export]);
        Assert(first.Added == 1 && store.Count == 1, "first import");
        Assert(store.Snapshot().Single().Category == "projekt", "category");
        var again = await store.ImportAsync([export]);
        Assert(again.Unchanged == 1 && store.Count == 1, "duplicate");
        var entry = store.Snapshot().Single();
        var messages = store.Messages(entry);
        Assert(messages.Count == 2 && messages[0].Role == "user", "active branch");
        Assert(messages.All(m => !m.Body.Contains("Nicht sichtbare", StringComparison.Ordinal)), "hidden content");
        var results = await store.SearchAsync(store.Snapshot(), "Nullmode", CancellationToken.None);
        Assert(results.Count == 1, "full text search");
        var findings = ResearchScanner.Scan(store, store.Snapshot());
        Assert(findings.Count > 0, "research findings");
        Assert(ResearchScanner.Handoff(findings).Contains("[HEURISTISCH]", StringComparison.Ordinal), "handoff");
        string backup = Path.Combine(root, "backup.zip");
        await store.BackupAsync(backup, null, CancellationToken.None);
        using (var zip = ZipFile.OpenRead(backup))
        {
            Assert(zip.GetEntry("conversations-000.json") != null, "backup conversations");
            Assert(zip.GetEntry("chatarchiv_manifest.json") != null, "backup manifest");
        }
        var restored = new ArchiveStore(Path.Combine(root, "restored"));
        var restoration = await restored.ImportAsync([backup]);
        Assert(restoration.Added == 1 && restored.Count == 1, "restore from backup");
    }

    private static void Assert(bool condition, string name)
    {
        if (!condition) throw new Exception("Smoke test failed: " + name);
    }
}
