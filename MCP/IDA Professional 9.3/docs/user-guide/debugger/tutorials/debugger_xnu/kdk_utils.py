import ida_idaapi
import ida_loader
import ida_ida
import ida_kernwin
import ida_netnode
import os

KDK_SUBMENU_PATH = "Edit/Other/KDK utils/"

# KDK-specific actions
KDK_ACTION_NAME_PFX  = "kdk_utils:"
KDK_ACTION_NAME_KDK  = KDK_ACTION_NAME_PFX  + "load_kdk"
KDK_ACTION_NAME_KEXT = KDK_ACTION_NAME_PFX  + "load_kext"

# pass arguments to the dwarf plugin via the database
DWARF_PARAM_NODE_NAME = "$ dwarf_params"
DWARF_PARAM_PATH_IDX  = 1

# dwarf plugin run codes
DWARF_RUN_CODE_KDK  = 4
DWARF_RUN_CODE_KEXT = 5

# invoke the dwarf plugin with a KDK-specific run code
class dwarf_loader_ah_t(ida_kernwin.action_handler_t):
    def __init__(self, prompt, code):
        ida_kernwin.action_handler_t.__init__(self)
        self.prompt = prompt
        self.code = code

    def update(self, ctx):
        return ida_kernwin.AST_ENABLE_ALWAYS

    def activate(self, ctx):
        path = ida_kernwin.ask_str("", 0, self.prompt)
        if path is None or len(path) == 0:
            return 0
        node = ida_netnode.netnode()
        node.create(DWARF_PARAM_NODE_NAME)
        node.supset(DWARF_PARAM_PATH_IDX, os.path.expanduser(path))
        ida_loader.load_and_run_plugin("dwarf", self.code)
        return 1

# PLUGIN object
class kdk_utils_t(ida_idaapi.plugin_t):
    flags = ida_idaapi.PLUGIN_HIDE
    comment = "Tools for working with an OSX Kernel Development Kit"
    help = comment
    wanted_name = "KDK utils"
    wanted_hotkey = ""

    def create_action(self, name, label, shortcut, prompt, code):
        handler = dwarf_loader_ah_t(prompt, code)
        desc = ida_kernwin.action_desc_t(name, label, handler, shortcut)
        ida_kernwin.register_action(desc)
        ida_kernwin.attach_action_to_menu(KDK_SUBMENU_PATH, name, 0)

    def init(self):
        if ida_ida.cvar.inf.filetype != ida_ida.f_MACHO:
            return ida_idaapi.PLUGIN_SKIP
        # this action will automatically detect all DWARF files in the given KDK
        # that match a subfile in the database (including the kernel itself),
        # and apply the DWARF info for each subfile.
        self.create_action(
                KDK_ACTION_NAME_KDK,
                "Load KDK",
                "Ctrl+Shift+K",
                "Enter a path to a KDK",
                DWARF_RUN_CODE_KDK)
        # this action is useful if there you have a prelinked kext that is not in Apple's KDK.
        # it will find the kext in the database that matches the given DWARF file,
        # and apply the DWARF info to this kext.
        self.create_action(
                KDK_ACTION_NAME_KEXT,
                "Load DWARF for a prelinked kext",
                "Ctrl+Shift+E",
                "Enter a path to a DWARF file",
                DWARF_RUN_CODE_KEXT)
        return ida_idaapi.PLUGIN_OK

    def run(self, arg):
        pass

    def term(self):
        pass

def PLUGIN_ENTRY():
    return kdk_utils_t()
