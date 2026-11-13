using System.Drawing;
using System.Text;
using System.Windows.Forms;

namespace UniverseLab.ChatArchiv.Win11;

public sealed class MainWindow : Form
{
    private static readonly Color Background = Color.FromArgb(8, 17, 28);
    private static readonly Color Panel = Color.FromArgb(21, 34, 48);
    private static readonly Color Accent = Color.FromArgb(116, 188, 244);
    private static readonly Color Foreground = Color.FromArgb(230, 239, 248);
    private static readonly Color Muted = Color.FromArgb(157, 180, 204);

    private readonly ArchiveStore _store = new();
    private readonly ListBox _list = new();
    private readonly RichTextBox _reader = new();
    private readonly TextBox _query = new();
    private readonly ComboBox _category = new();
    private readonly Label _status = new();
    private readonly Label _heading = new();
    private readonly Label _subheading = new();
    private readonly List<Button> _busyButtons = [];
    private List<ArchiveEntry>? _searchResults;
    private List<VisibleMessage> _currentMessages = [];
    private ArchiveEntry? _current;
    private bool _busy;

    private sealed record ChatRow(ArchiveEntry Entry)
    {
        public override string ToString() => $"{Entry.Date}   {Entry.Title}";
    }

    public MainWindow()
    {
        Text = "UniverseLab ChatArchiv – Windows 11 (0.1.0)";
        StartPosition = FormStartPosition.CenterScreen;
        MinimumSize = new Size(850, 580);
        Size = new Size(1280, 820);
        BackColor = Background;
        ForeColor = Foreground;
        Font = new Font("Segoe UI", 10f);

        var top = new TableLayoutPanel { Dock = DockStyle.Top, Height = 110, ColumnCount = 1, BackColor = Background };
        top.RowStyles.Add(new RowStyle(SizeType.Absolute, 48));
        top.RowStyles.Add(new RowStyle(SizeType.Absolute, 56));
        var title = new Label
        {
            Text = "UniverseLab  ·  ChatArchiv   |   Windows 11",
            Font = new Font("Segoe UI Semibold", 18), ForeColor = Foreground,
            Dock = DockStyle.Fill, TextAlign = ContentAlignment.MiddleLeft, Padding = new Padding(15, 0, 0, 0)
        };
        top.Controls.Add(title, 0, 0);

        var toolbar = new FlowLayoutPanel
        {
            Dock = DockStyle.Fill, FlowDirection = FlowDirection.LeftToRight, AutoScroll = true,
            WrapContents = false, Padding = new Padding(10, 3, 6, 3)
        };
        toolbar.Controls.Add(CreateButton("JSON / ZIP importieren", async (_, _) => await ImportFiles()));
        toolbar.Controls.Add(CreateButton("Ordner durchsuchen", async (_, _) => await ImportFolder()));
        toolbar.Controls.Add(CreateButton("Volltext suchen", async (_, _) => await Search()));
        toolbar.Controls.Add(CreateButton("Forschungsnavigator", async (_, _) => await OpenNavigator()));
        toolbar.Controls.Add(CreateButton("Chat exportieren", (_, _) => ExportSelected()));
        toolbar.Controls.Add(CreateButton("Archiv als ZIP sichern", async (_, _) => await Backup()));
        top.Controls.Add(toolbar, 0, 1);

        var footer = new Panel { Dock = DockStyle.Bottom, Height = 35, BackColor = Panel };
        _status.Dock = DockStyle.Fill;
        _status.ForeColor = Accent;
        _status.TextAlign = ContentAlignment.MiddleLeft;
        _status.Padding = new Padding(12, 0, 0, 0);
        footer.Controls.Add(_status);

        var split = new SplitContainer
        {
            Dock = DockStyle.Fill, Orientation = Orientation.Vertical, SplitterWidth = 7,
            SplitterDistance = 390, BackColor = Background, Panel1MinSize = 280, Panel2MinSize = 400
        };

        var leftTop = new TableLayoutPanel { Dock = DockStyle.Top, Height = 108, ColumnCount = 1, Padding = new Padding(8) };
        leftTop.RowStyles.Add(new RowStyle(SizeType.Absolute, 44));
        leftTop.RowStyles.Add(new RowStyle(SizeType.Absolute, 45));
        _query.Dock = DockStyle.Fill;
        _query.BackColor = Panel;
        _query.ForeColor = Foreground;
        _query.BorderStyle = BorderStyle.FixedSingle;
        _query.PlaceholderText = "Suchbegriff eingeben, dann Volltext suchen …";
        _query.KeyDown += async (_, args) =>
        {
            if (args.KeyCode == Keys.Enter) { args.SuppressKeyPress = true; await Search(); }
        };
        leftTop.Controls.Add(_query, 0, 0);

        _category.Dock = DockStyle.Fill;
        _category.DropDownStyle = ComboBoxStyle.DropDownList;
        _category.FlatStyle = FlatStyle.Flat;
        _category.BackColor = Panel;
        _category.ForeColor = Foreground;
        _category.Items.AddRange(["Alle Chats", "UniverseLab", "Weitere Chats"]);
        _category.SelectedIndex = 0;
        _category.SelectedIndexChanged += (_, _) => PopulateList();
        leftTop.Controls.Add(_category, 0, 1);

        var leftBottom = new FlowLayoutPanel
        {
            Dock = DockStyle.Bottom, Height = 50, Padding = new Padding(5), WrapContents = false
        };
        leftBottom.Controls.Add(CreateButton("→ UniverseLab", (_, _) => ChangeCategory("projekt")));
        leftBottom.Controls.Add(CreateButton("→ Weitere", (_, _) => ChangeCategory("andere")));
        _list.Dock = DockStyle.Fill;
        _list.BackColor = Panel;
        _list.ForeColor = Foreground;
        _list.BorderStyle = BorderStyle.None;
        _list.IntegralHeight = false;
        _list.HorizontalScrollbar = true;
        _list.ItemHeight = 27;
        _list.SelectedIndexChanged += (_, _) => ShowSelected();
        split.Panel1.Controls.Add(_list);
        split.Panel1.Controls.Add(leftTop);
        split.Panel1.Controls.Add(leftBottom);

        var info = new Panel { Dock = DockStyle.Top, Height = 87, Padding = new Padding(14, 5, 5, 5) };
        _heading.Text = "Gespräch auswählen";
        _heading.Font = new Font("Segoe UI Semibold", 15f);
        _heading.ForeColor = Accent;
        _heading.Dock = DockStyle.Top;
        _heading.Height = 44;
        _subheading.Text = "Originaler sichtbarer Gesprächspfad · keine Cloudverbindung";
        _subheading.ForeColor = Muted;
        _subheading.Dock = DockStyle.Top;
        _subheading.Height = 32;
        info.Controls.Add(_subheading);
        info.Controls.Add(_heading);

        var readerBottom = new FlowLayoutPanel
        {
            Dock = DockStyle.Bottom, Height = 47, Padding = new Padding(8, 2, 0, 0), WrapContents = false
        };
        readerBottom.Controls.Add(CreateButton("Gespräch kopieren", (_, _) => CopyChat()));
        readerBottom.Controls.Add(CreateButton("JSON-Original exportieren", (_, _) => ExportSelected(forceJson: true)));
        _reader.Dock = DockStyle.Fill;
        _reader.ReadOnly = true;
        _reader.BorderStyle = BorderStyle.None;
        _reader.BackColor = Panel;
        _reader.ForeColor = Foreground;
        _reader.Font = new Font("Segoe UI", 11f);
        _reader.ScrollBars = RichTextBoxScrollBars.Vertical;
        _reader.WordWrap = true;
        _reader.DetectUrls = false;
        split.Panel2.Controls.Add(_reader);
        split.Panel2.Controls.Add(info);
        split.Panel2.Controls.Add(readerBottom);

        Controls.Add(split);
        Controls.Add(top);
        Controls.Add(footer);
        SetStatus($"Lokal gespeichert: {_store.Count} Chats. Keine Anmeldung und keine Datenübertragung.");
        PopulateList();
    }

    private Button CreateButton(string text, EventHandler handler)
    {
        var button = new Button
        {
            Text = text, Height = 39, AutoSize = true, Margin = new Padding(4),
            Padding = new Padding(11, 2, 11, 2), FlatStyle = FlatStyle.Flat,
            BackColor = Panel, ForeColor = Accent, Cursor = Cursors.Hand
        };
        button.FlatAppearance.BorderColor = Accent;
        button.FlatAppearance.BorderSize = 1;
        button.Click += handler;
        _busyButtons.Add(button);
        return button;
    }

    private void SetStatus(string value) => _status.Text = value;

    private void PopulateList()
    {
        string? previousId = (_list.SelectedItem as ChatRow)?.Entry.Id;
        var entries = (_searchResults ?? _store.Snapshot()).Where(entry => _category.SelectedIndex switch
        {
            1 => entry.Category == "projekt", 2 => entry.Category == "andere", _ => true
        }).ToList();
        _list.BeginUpdate();
        _list.Items.Clear();
        foreach (var entry in entries) _list.Items.Add(new ChatRow(entry));
        _list.EndUpdate();
        if (previousId != null)
            for (int i = 0; i < _list.Items.Count; i++)
                if ((_list.Items[i] as ChatRow)?.Entry.Id == previousId) { _list.SelectedIndex = i; break; }
        SetStatus($"{entries.Count} Chats angezeigt · {_store.Count} lokal gespeichert · vollständig offline");
    }

    private void ShowSelected()
    {
        if (_list.SelectedItem is not ChatRow row) return;
        _current = row.Entry;
        try
        {
            _currentMessages = _store.Messages(row.Entry);
            _heading.Text = row.Entry.Title;
            _subheading.Text = $"{row.Entry.Date}  ·  {_currentMessages.Count} sichtbare Beiträge  ·  {row.Entry.Id}";
            var contents = ArchiveStore.Markdown(row.Entry, _currentMessages);
            if (contents.Length > 2_000_000)
                contents = contents[..2_000_000] + "\n\n[Anzeige auf 2 Mio. Zeichen begrenzt. Export enthält alle Beiträge.]";
            _reader.Text = contents;
            _reader.SelectionStart = 0;
            _reader.ScrollToCaret();
        }
        catch (Exception exception) { ShowError("Gespräch nicht lesbar", exception); }
    }

    private void ChangeCategory(string category)
    {
        if (_list.SelectedItem is not ChatRow row) return;
        _store.SetCategory(row.Entry.Id, category);
        PopulateList();
    }

    private void MarkBusy(bool value)
    {
        _busy = value;
        foreach (var button in _busyButtons) button.Enabled = !value;
        _category.Enabled = !value;
    }

    private async Task ImportFiles()
    {
        if (_busy) return;
        using var picker = new OpenFileDialog
        {
            Filter = "ChatGPT-Exporte (*.json;*.zip)|*.json;*.zip|Alle Dateien (*.*)|*.*",
            Multiselect = true, Title = "ChatGPT conversations*.json oder Export-ZIP auswählen"
        };
        if (picker.ShowDialog(this) != DialogResult.OK) return;
        await ImportSelected(picker.FileNames);
    }

    private async Task ImportFolder()
    {
        if (_busy) return;
        using var picker = new FolderBrowserDialog { Description = "Einmal einen Ordner auswählen; Unterordner werden rekursiv durchsucht" };
        if (picker.ShowDialog(this) != DialogResult.OK) return;
        string[] files;
        try
        {
            files = await Task.Run(() => Directory.EnumerateFiles(picker.SelectedPath, "*.*", SearchOption.AllDirectories)
                .Where(file => ArchiveStore.IsConversationJson(Path.GetFileName(file)) ||
                    file.EndsWith(".zip", StringComparison.OrdinalIgnoreCase)).ToArray());
        }
        catch (Exception exception) { ShowError("Ordner konnte nicht durchsucht werden", exception); return; }
        if (files.Length == 0) { MessageBox.Show(this, "Keine conversations*.json oder ZIP-Dateien gefunden."); return; }
        if (MessageBox.Show(this, $"{files.Length} potenzielle Exportdateien gefunden.\n\nJetzt lokal importieren?",
                "Import bestätigen", MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return;
        await ImportSelected(files);
    }

    private async Task ImportSelected(IEnumerable<string> files)
    {
        MarkBusy(true);
        try
        {
            SetStatus("Import läuft …");
            var progress = new Progress<ImportCounts>(counts => SetStatus("Import: " + counts));
            var counts = await Task.Run(() => _store.ImportAsync(files,
                value => ((IProgress<ImportCounts>)progress).Report(value)));
            _searchResults = null;
            PopulateList();
            MessageBox.Show(this, counts + $"\n\nGesamter Chatbestand: {_store.Count}", "Import abgeschlossen",
                MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception exception) { ShowError("Import nicht vollständig", exception); }
        finally { MarkBusy(false); PopulateList(); }
    }

    private async Task Search()
    {
        if (_busy) return;
        string query = _query.Text.Trim();
        if (query.Length == 0) { _searchResults = null; PopulateList(); return; }
        MarkBusy(true);
        SetStatus($"Suche in {_store.Count} Chats nach „{query}“ …");
        try
        {
            _searchResults = await Task.Run(() => _store.SearchAsync(_store.Snapshot(), query,
                CancellationToken.None));
            PopulateList();
        }
        catch (Exception exception) { ShowError("Suche fehlgeschlagen", exception); }
        finally { MarkBusy(false); }
    }

    private void CopyChat()
    {
        if (_current == null) return;
        Clipboard.SetText(ArchiveStore.Markdown(_current, _currentMessages));
        SetStatus("Vollständiger sichtbarer Gesprächspfad in die Zwischenablage kopiert");
    }

    private void ExportSelected(bool forceJson = false)
    {
        if (_current == null) { MessageBox.Show(this, "Bitte zuerst einen Chat auswählen."); return; }
        using var dialog = new SaveFileDialog
        {
            FileName = SafeName(_current.Title),
            Filter = forceJson ? "JSON-Original (*.json)|*.json" :
                "Markdown (*.md)|*.md|Text (*.txt)|*.txt|HTML (*.html)|*.html|JSON-Original (*.json)|*.json"
        };
        if (dialog.ShowDialog(this) != DialogResult.OK) return;
        try
        {
            string extension = Path.GetExtension(dialog.FileName).ToLowerInvariant();
            string content = extension switch
            {
                ".json" => _store.OriginalJson(_current),
                ".html" => HtmlExport(_current, _currentMessages),
                _ => ArchiveStore.Markdown(_current, _currentMessages)
            };
            File.WriteAllText(dialog.FileName, content, new UTF8Encoding(false));
            SetStatus("Chat gespeichert: " + dialog.FileName);
        }
        catch (Exception exception) { ShowError("Export fehlgeschlagen", exception); }
    }

    private static string SafeName(string name)
    {
        foreach (char invalid in Path.GetInvalidFileNameChars()) name = name.Replace(invalid, '_');
        return name.Length > 80 ? name[..80] : name;
    }

    private static string HtmlExport(ArchiveEntry item, IReadOnlyList<VisibleMessage> messages)
    {
        var sb = new StringBuilder("<!doctype html><html lang=\"de\"><meta charset=\"utf-8\">");
        sb.Append("<title>").Append(System.Net.WebUtility.HtmlEncode(item.Title)).Append("</title>")
            .Append("<style>body{max-width:1000px;margin:2em auto;padding:1em;background:#08111c;color:#e6eff8;font:18px Segoe UI,sans-serif}article{background:#152230;border-radius:9px;padding:1em;margin:1em 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}h2{color:#74bcf4}</style>")
            .Append("<h1>").Append(System.Net.WebUtility.HtmlEncode(item.Title)).Append("</h1>");
        for (int i = 0; i < messages.Count; i++)
            sb.Append("<article><h2>").Append(i + 1).Append(". ").Append(messages[i].Role)
                .Append("</h2><pre>").Append(System.Net.WebUtility.HtmlEncode(messages[i].Body))
                .Append("</pre></article>");
        return sb.Append("</html>").ToString();
    }

    private async Task Backup()
    {
        if (_busy) return;
        using var dialog = new SaveFileDialog
        {
            Filter = "ZIP-Archiv (*.zip)|*.zip",
            FileName = $"UniverseLab-ChatArchiv-Win11-{DateTime.Now:yyyy-MM-dd}.zip"
        };
        if (dialog.ShowDialog(this) != DialogResult.OK) return;
        MarkBusy(true);
        try
        {
            var report = new Progress<(int, int)>(tuple => SetStatus($"ZIP-Sicherung: {tuple.Item1}/{tuple.Item2}"));
            await Task.Run(() => _store.BackupAsync(dialog.FileName,
                (done, total) => ((IProgress<(int, int)>)report).Report((done, total)), CancellationToken.None));
            MessageBox.Show(this, "Archiv lokal gesichert.\n\n" + dialog.FileName,
                "ZIP-Sicherung abgeschlossen", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception exception) { ShowError("ZIP-Sicherung fehlgeschlagen", exception); }
        finally { MarkBusy(false); }
    }

    private async Task OpenNavigator()
    {
        if (_busy) return;
        var source = _store.Snapshot();
        if (source.Count == 0) { MessageBox.Show(this, "Noch keine passenden Chats importiert."); return; }
        bool allChats = MessageBox.Show(this,
            $"Forschungsnavigator starten?\n\nJa = alle {_store.Count} Chats\nNein = nur UniverseLab-Chats\n\nAlle Hinweise sind [HEURISTISCH].",
            "Prüfbereich", MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes;
        source = allChats ? _store.Snapshot() : _store.Snapshot().Where(e => e.Category == "projekt").ToList();
        MarkBusy(true);
        List<ResearchFinding> findings;
        try
        {
            var report = new Progress<(int, int)>(tuple => SetStatus($"Forschungsnavigator: {tuple.Item1}/{tuple.Item2} Chats …"));
            findings = await Task.Run(() => ResearchScanner.Scan(_store, source,
                (done, total) => ((IProgress<(int, int)>)report).Report((done, total))));
        }
        catch (Exception exception) { ShowError("Prüfung fehlgeschlagen", exception); return; }
        finally { MarkBusy(false); }
        using var browser = new FindingsWindow(findings, id => SelectById(id));
        browser.ShowDialog(this);
    }

    private void SelectById(string id)
    {
        _searchResults = null;
        _category.SelectedIndex = 0;
        PopulateList();
        for (int i = 0; i < _list.Items.Count; i++)
            if ((_list.Items[i] as ChatRow)?.Entry.Id == id)
            {
                _list.SelectedIndex = i;
                _list.TopIndex = Math.Max(0, i - 2);
                return;
            }
    }

    private void ShowError(string caption, Exception exception)
    {
        MessageBox.Show(this, exception.Message, caption, MessageBoxButtons.OK, MessageBoxIcon.Warning);
        SetStatus(caption + ": " + exception.Message);
    }
}

public sealed class FindingsWindow : Form
{
    private readonly ListView _list = new();
    private readonly RichTextBox _details = new();
    private readonly List<ResearchFinding> _findings;
    private readonly Action<string> _openChat;

    public FindingsWindow(List<ResearchFinding> findings, Action<string> openChat)
    {
        _findings = findings;
        _openChat = openChat;
        Text = "UniverseLab – Forschungsnavigator [HEURISTISCH]";
        Width = 1100;
        Height = 750;
        StartPosition = FormStartPosition.CenterParent;
        BackColor = Color.FromArgb(8, 17, 28);
        ForeColor = Color.FromArgb(230, 239, 248);
        Font = new Font("Segoe UI", 10f);
        var label = new Label
        {
            Dock = DockStyle.Top, Height = 55, ForeColor = Color.FromArgb(116, 188, 244),
            Padding = new Padding(10, 8, 0, 0),
            Text = $"{findings.Count} heuristische Hinweise · historische Aussagen, nicht bestätigte heutige Forschungslücken"
        };
        _list.Dock = DockStyle.Top;
        _list.Height = 290;
        _list.View = View.Details;
        _list.FullRowSelect = true;
        _list.CheckBoxes = true;
        _list.BackColor = Color.FromArgb(21, 34, 48);
        _list.ForeColor = ForeColor;
        _list.Columns.Add("Art", 130);
        _list.Columns.Add("Quellchat", 490);
        _list.Columns.Add("Beitrag", 85);
        _list.Columns.Add("Signal", 180);
        foreach (var finding in findings)
        {
            var item = new ListViewItem([finding.Kind, finding.ChatTitle, finding.Number.ToString(), finding.Signal])
            {
                Tag = finding, Checked = false
            };
            _list.Items.Add(item);
        }
        _list.SelectedIndexChanged += (_, _) => ShowFinding();
        _list.DoubleClick += (_, _) => OpenSelected();

        _details.Dock = DockStyle.Fill;
        _details.ReadOnly = true;
        _details.BackColor = Color.FromArgb(21, 34, 48);
        _details.ForeColor = ForeColor;
        _details.BorderStyle = BorderStyle.None;
        _details.Font = new Font("Segoe UI", 11f);
        var bottom = new FlowLayoutPanel { Dock = DockStyle.Bottom, Height = 60, Padding = new Padding(8) };
        bottom.Controls.Add(MakeButton("Quellchat öffnen", (_, _) => OpenSelected()));
        bottom.Controls.Add(MakeButton("Erste 12 markieren", (_, _) =>
        {
            for (int i = 0; i < _list.Items.Count; i++) _list.Items[i].Checked = i < 12;
        }));
        bottom.Controls.Add(MakeButton("Übergabe kopieren", (_, _) =>
        {
            var selected = _list.CheckedItems.Cast<ListViewItem>().Select(item => (ResearchFinding)item.Tag!).Take(12).ToList();
            if (selected.Count == 0) { MessageBox.Show(this, "Bitte bis zu 12 Fundstellen ankreuzen."); return; }
            Clipboard.SetText(ResearchScanner.Handoff(selected));
            MessageBox.Show(this, $"{selected.Count} Fundstellen für einen neuen Chat kopiert.");
        }));
        bottom.Controls.Add(MakeButton("Übergabe speichern", (_, _) =>
        {
            var selected = _list.CheckedItems.Cast<ListViewItem>().Select(item => (ResearchFinding)item.Tag!).Take(12).ToList();
            if (selected.Count == 0) { MessageBox.Show(this, "Bitte Fundstellen ankreuzen."); return; }
            using var picker = new SaveFileDialog { FileName = "UniverseLab-Uebergabe.md", Filter = "Markdown (*.md)|*.md" };
            if (picker.ShowDialog(this) == DialogResult.OK)
                File.WriteAllText(picker.FileName, ResearchScanner.Handoff(selected), new UTF8Encoding(false));
        }));
        Controls.Add(_details);
        Controls.Add(bottom);
        Controls.Add(_list);
        Controls.Add(label);
    }

    private Button MakeButton(string title, EventHandler action)
    {
        var button = new Button
        {
            Text = title, Height = 38, AutoSize = true, Padding = new Padding(9, 1, 9, 1),
            BackColor = Color.FromArgb(21, 34, 48), ForeColor = Color.FromArgb(116, 188, 244),
            FlatStyle = FlatStyle.Flat
        };
        button.Click += action;
        return button;
    }

    private void ShowFinding()
    {
        if (_list.SelectedItems.Count == 0) return;
        var finding = (ResearchFinding)_list.SelectedItems[0].Tag!;
        _details.Text = $"[{finding.Kind}] {finding.ChatTitle}\n\n"
            + $"Chat-ID: {finding.ChatId}\nBeitrag: {finding.Number} ({finding.Role})\nSignal: {finding.Signal}\n\n"
            + finding.Excerpt + "\n\n[HEURISTISCH] Stand nicht verifiziert. Originalchat und aktuellen Kanon abgleichen.";
    }

    private void OpenSelected()
    {
        if (_list.SelectedItems.Count == 0) return;
        string id = ((ResearchFinding)_list.SelectedItems[0].Tag!).ChatId;
        Close();
        _openChat(id);
    }
}
