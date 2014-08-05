import sublime, sublime_plugin
import subprocess, os

# https://github.com/int3h/SublimeFixMacPath/blob/master/FixPath.py
def sys_env(var):
    command = "/usr/bin/login -fpql $USER $SHELL -l -c 'echo -n $" + var+ "'"
    output = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
    return output.decode("utf-8")

def my_env():
    env = os.environ.copy()
    env["PATH"] = sys_env("PATH")
    env["LANG"] = sys_env("LANG")
    return env

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
        
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env())
        (output, err) = p.communicate()
        p.wait()
        os.chdir(old_dir)
        if p.returncode==0:
            sublime.status_message("Build Succeed.")
        else:
            sublime.status_message("Build Failed.")
            print(err.decode('utf-8'))
