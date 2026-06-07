# DomainForge demo — render with: vhs demo.tape   (https://github.com/charmbracelet/vhs)
# Produces examples/demo.gif used at the top of the README.
#
# Prereq: the `domainforge` CLI must be on PATH in the shell vhs spawns. Install
# first:  pipx install '.[recommended]'   (or, for dev:  pip install -e .)
# (We use the `domainforge` command, not `python`/`python3`, so the GIF works on
#  any machine regardless of how Python is named.)

Output examples/demo.gif

Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 760
Set Padding 24
Set Theme "Catppuccin Mocha"

Type "# DomainForge — find available, brandable domains in one command"
Enter
Sleep 1s

Type "domainforge --fast --base 'rune,forge' --check 12 -y"
Sleep 800ms
Enter

# Generation is near-instant on --fast; the live availability check streams in.
Sleep 30s
