#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <mach-o/dyld.h>
#include <libgen.h>

#ifndef DEFAULT_PROJECT_DIR
#define DEFAULT_PROJECT_DIR "/Users/victoredier/Code/my_call_recorder_on_mac"
#endif

int main(int argc, char *argv[]) {
    char exec_path[1024];
    uint32_t size = sizeof(exec_path);
    if (_NSGetExecutablePath(exec_path, &size) != 0) {
        fprintf(stderr, "Error: buffer too small for executable path\n");
        return 1;
    }
    
    char real_path[1024];
    if (realpath(exec_path, real_path) == NULL) {
        perror("realpath");
        return 1;
    }

    // Determine project directory:
    // If the .app is inside the project directory, resolve dynamically.
    // If moved to /Applications or Desktop, fall back to DEFAULT_PROJECT_DIR.
    const char *project_dir = DEFAULT_PROJECT_DIR;
    char path_copy[1024];
    strncpy(path_copy, real_path, sizeof(path_copy));
    char *dir1 = dirname(path_copy); // Contents/MacOS
    char *dir2 = dirname(dir1);       // Contents
    char *dir3 = dirname(dir2);       // Call Recorder.app
    char *dir4 = dirname(dir3);       // Containing directory

    char check_main[1024];
    snprintf(check_main, sizeof(check_main), "%s/main.py", dir4);
    if (access(check_main, F_OK) == 0) {
        project_dir = dir4;
    }

    if (chdir(project_dir) != 0) {
        perror("chdir project_dir");
        return 1;
    }

    // Initialize Python runtime embedded in Call Recorder.app bundle
    Py_Initialize();

    wchar_t *wargv[argc + 1];
    wargv[0] = Py_DecodeLocale("Call Recorder", NULL);
    for (int i = 1; i < argc; i++) {
        wargv[i] = Py_DecodeLocale(argv[i], NULL);
    }
    wargv[argc] = NULL;
    PySys_SetArgv(argc, wargv);

    char pycode[4096];
    snprintf(pycode, sizeof(pycode),
        "import sys, os, glob\n"
        "pdir = '%s'\n"
        "for sp in glob.glob(os.path.join(pdir, 'venv', 'lib', 'python3.*', 'site-packages')):\n"
        "    if sp not in sys.path:\n"
        "        sys.path.insert(0, sp)\n"
        "if pdir not in sys.path:\n"
        "    sys.path.insert(0, pdir)\n"
        "os.chdir(pdir)\n"
        "main_file = os.path.join(pdir, 'main.py')\n"
        "with open(main_file, 'rb') as f:\n"
        "    code = compile(f.read(), main_file, 'exec')\n"
        "    exec(code, {'__name__': '__main__', '__file__': main_file})\n",
        project_dir
    );

    int res = PyRun_SimpleString(pycode);
    Py_Finalize();
    return res;
}
