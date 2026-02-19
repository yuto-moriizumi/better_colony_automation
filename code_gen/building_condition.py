import copy

from synthetipy.parser import parse
from synthetipy.script_merger import utils
from synthetipy.ast_loadder import ASTLoader
from synthetipy.ast_nodes import *
from pathlib import Path
from synthetipy.compiler import compile_to_file


CONFIG = {
    'common': {
        "buildings"
    },
}

GAME_ROOT = Path("D:\SteamLibrary\steamapps\common\Stellaris")

ast = ASTLoader(GAME_ROOT, CONFIG).load()

out_file = DocumentNode([])

def remove_from_block(node:BlockNode):
    parent:PropertyNode = node.parent
    grand_parent:BlockNode = parent.parent
    grand_parent.statements.remove(parent)

def template(building:ObjectNode,
             potential:BlockNode,
             allow:BlockNode,
             abort_trigger:BlockNode,
             prerequisites:Union[ListNode,BlockNode]
             ):
    template_code = r"""
bca_can_build_$BUILDING$ = {
    AND = {$potential$}
    AND = {$allow$}
    NOR = {$abort_trigger$}
    owner = {
        $prerequisites$
        has_technology = xx
    }
}
"""
    template_ast = parse(template_code)
    obj:ObjectNode = template_ast.statements[0]  # 获取根对象
    obj.name.macro_expression = None
    obj.name.identifier = IdentifierNode(f"bca_can_build_{building.name.identifier}")

    def replace_macro(node:ASTNode, parent:ASTNode):
        for c in utils.astnode_children(node):
            replace_macro(c, node)
        if isinstance(node, IdentifierExpressionNode):
            if not node.macro_expression: return
            param_name = node.macro_expression.macro_params[0].name
            if param_name == "potential":
                if not potential or len(potential.statements) == 0:
                    remove_from_block(parent)
                    return
                parent.statements = potential.statements
            elif param_name == "allow":
                if not allow or len(allow.statements) == 0:
                    remove_from_block(parent)
                    return
                parent.statements = allow.statements
            elif param_name == "abort_trigger":
                if not abort_trigger or len(abort_trigger.statements) == 0:
                    remove_from_block(parent)
                    return
                parent.statements = abort_trigger.statements
            elif param_name == "prerequisites":
                if not prerequisites or isinstance(prerequisites, BlockNode) and len(prerequisites.statements) == 0:
                    remove_from_block(parent)
                    return
                temp1:PropertyNode = parent.statements[1]
                parent.statements.clear()
                for item in prerequisites.items:
                    temp_copy = copy.deepcopy(temp1)
                    temp_copy.value = item
                    parent.statements.append(temp_copy)

    replace_macro(obj, None)
    return obj


for name, zone in ast['common/buildings'].items():
    potential = None
    allow = None
    abort_trigger = None
    prerequisites = None
    for stat in zone.body.statements:
        if not isinstance(stat, PropertyNode): continue
        if str(stat.key) == 'potential':
            potential = stat.value
        elif str(stat.key) == 'allow':
            allow = stat.value
        elif str(stat.key) == 'abort_trigger':
            abort_trigger = stat.value
        elif str(stat.key) == 'prerequisites':
            prerequisites = stat.value
    out_file.statements.append(template(zone, potential, allow, abort_trigger, prerequisites))

compile_to_file(out_file, "../common/scripted_triggers/building_build_conditions.txt")



