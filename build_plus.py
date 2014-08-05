import sublime, sublime_plugin
import subprocess, os

# https://github.com/int3h/SublimeFixMacPath/blob/master/FixPath.py
def getSysPath():
    command = "/usr/bin/login -fpql $USER $SHELL -l -c 'echo -n $PATH'"

    # Execute command with original environ. Otherwise, our changes to the PATH propogate down to
    # the shell we spawn, which re-adds the system path & returns it, leading to duplicate values.
    sysPath = subprocess.Popen(command, stdout=subprocess.PIPE,
        shell=True).stdout.read()

    # Decode the byte array into a string, remove trailing whitespace, remove trailing ':'
    return sysPath.decode("utf-8").rstrip().rstrip(':')

def getenv():
    my_env = os.environ.copy()
    my_env["PATH"] = getSysPath() + ":" + my_env["PATH"]
    my_env["LANG"] = "en_US.UTF-8"
    return my_env

class BuildPlusCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()

        file_name = view.file_name()
        file_dir = os.path.dirname(file_name)
        old_dir = os.getcwd()
        os.chdir(file_dir)

        r = view.find(r"(?<=\[cmd\])(.|\n)*?(?=\[/cmd\])", 0)
        if not r: return
        cmd = view.substr(r)

        cmd = cmd.strip().replace("\n", "")
        if not cmd: return
        # print(cmd)
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=getenv())
        (output, err) = p.communicate()
        p.wait()
        os.chdir(old_dir)
        if p.returncode==0:
            sublime.status_message("Build Succeed.")
        else:
            sublime.status_message("Build Failed.")
            print(err.decode('utf-8'))
