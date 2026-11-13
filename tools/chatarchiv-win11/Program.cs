using System.Windows.Forms;

namespace UniverseLab.ChatArchiv.Win11;

internal static class Program
{
    [STAThread]
    private static int Main(string[] args)
    {
        if (args.Contains("--self-test", StringComparer.OrdinalIgnoreCase))
            return SmokeTests.Run();

        ApplicationConfiguration.Initialize();
        Application.Run(new MainWindow());
        return 0;
    }
}
