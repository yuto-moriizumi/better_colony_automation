from synthetipy.parser import parse
from synthetipy.script_merger import utils
from synthetipy.ast_loadder import ASTLoader
from synthetipy.ast_nodes import *
from pathlib import Path
from synthetipy.compiler import compile_to_file
import copy


CONFIG = {
    'common': {
        "districts",
        "zone_slots",
        "zones"
    },
}

GAME_ROOT = Path("D:\SteamLibrary\steamapps\common\Stellaris")

ast = ASTLoader(GAME_ROOT, CONFIG).load()

out_file = DocumentNode([])

def remove_from_block(node:BlockNode):
    parent:PropertyNode = node.parent
    grand_parent:BlockNode = parent.parent
    grand_parent.statements.remove(parent)

district_type_mapping = {}
# zone_slot -> List[district]
zone_slot_mapping: Dict[str, List[str]] = {}
for name, zone in ast['common/districts'].items():
    for stat in zone.body.statements:
        if not isinstance(stat, PropertyNode): continue
        if str(stat.key) == 'zone_slots':
            if not isinstance(stat.value, ListNode):
                raise ValueError(f"Expected list for zone_slots in district {name}")
            for zone_slot in stat.value.items:
                zone_slot_mapping.setdefault(str(zone_slot), []).append(name)
            if len(stat.value.items) == 1:
                district_type_mapping[name] = "single_zone"
            else:
                district_type_mapping[name] = "multi_zone"

# zone_set -> zone_slot
zone_set_zone_slot_mapping: Dict[str, List[str]] = {}
for name, zone in ast['common/zone_slots'].items():
    # zone_sets
    for stat in zone.body.statements:
        if not isinstance(stat, PropertyNode): continue
        if str(stat.key) == 'included_zone_sets':
            if not isinstance(stat.value, ListNode):
                raise ValueError(f"Expected list for zone_slots in zone {name}")
            for zone_set in stat.value.items:
                zone_set_zone_slot_mapping.setdefault(str(zone_set), []).append(name)

# zone -> zone_set
zone_zone_slot_mapping: Dict[str, List[str]] = {}
for name, zone in ast['common/zones'].items():
    # zone_sets
    for stat in zone.body.statements:
        if not isinstance(stat, PropertyNode): continue
        if str(stat.key) == 'zone_sets':
            if not isinstance(stat.value, ListNode):
                raise ValueError(f"Expected list for zone_slots in zone {name}")
            for zone_slot in stat.value.items:
                zone_zone_slot_mapping.setdefault(name, []).append(str(zone_slot))

zone_zone_slot_mapping.pop('zone_default', None)  # 移除默认的 zone_default

# zone -> List[district]
zone_district_mapping: Dict[str, List[str]] = {}
for zone, zone_sets in zone_zone_slot_mapping.items():
    for zone_set in zone_sets:
        zone_slots = zone_set_zone_slot_mapping.get(zone_set)
        if not zone_slots:
            print(f"Zone set [{zone_set}] has no associated zone slots")
            continue
        for zone_slot in zone_slots:
            districts = zone_slot_mapping.get(zone_slot)
            if not districts:
                print(f"Zone slot [{zone_slot}] has no associated districts")
                continue
            zone_district_mapping.setdefault(zone, []).extend(districts)


def template(zone:ObjectNode, zone_potential:BlockNode, zone_unlock:BlockNode, show_in_tech:ASTNode):
    template_code = r"""
bca_can_build_$ZONE$ = {
    AND = {$potential$}
    AND = {$UNLOCK$}
    owner = {
        $show_in_tech$
        has_technology = xx
    }
}
"""
    template_ast = parse(template_code)
    obj:ObjectNode = template_ast.statements[0]  # 获取根对象
    obj.name.macro_expression = None
    obj.name.identifier = IdentifierNode(f"bca_can_build_{zone.name.identifier}")

    def replace_macro(node:ASTNode, parent:ASTNode):
        for c in utils.astnode_children(node):
            replace_macro(c, node)
        if isinstance(node, IdentifierExpressionNode):
            if not node.macro_expression: return
            param_name = node.macro_expression.macro_params[0].name
            if param_name == "potential":
                if not zone_potential or len(zone_potential.statements) == 0:
                    remove_from_block(parent)
                    return
                parent.statements = zone_potential.statements
            elif param_name == "UNLOCK":
                if not zone_unlock or len(zone_unlock.statements) == 0:
                    remove_from_block(parent)
                    return
                parent.statements = zone_unlock.statements
            elif param_name == "show_in_tech":
                if not show_in_tech:
                    remove_from_block(parent)
                    return
                temp1:PropertyNode = parent.statements[1]
                parent.statements.clear()
                temp1.value = show_in_tech
                parent.statements.append(temp1)
            # elif param_name == "zone_sets":
            #     temp1:PropertyNode = parent.statements[1]
            #     parent.statements.clear()
            #     zone_name = str(zone.name)
            #     district_list = zone_district_mapping.get(zone_name)
            #     if not district_list:
            #         print(f"Zone [{zone_name}] has no associated districts")
            #         return
            #     for district in district_list:
            #         temp_copy = copy.copy(temp1)
            #         temp_copy.value = IdentifierExpressionNode()
            #         temp_copy.value.identifier = IdentifierNode(district)
            #         parent.statements.append(temp_copy)
            #     if len(parent.statements) == 0:
            #         remove_from_block(parent)

    replace_macro(obj, None)
    return obj

for name, zone in ast['common/zones'].items():
    potential = None
    zone_unlock = None
    show_in_tech = None
    for stat in zone.body.statements:
        if not isinstance(stat, PropertyNode): continue
        if str(stat.key) == 'potential':
            potential = stat.value
        elif str(stat.key) == 'unlock':
            zone_unlock = stat.value
        elif str(stat.key) == 'show_in_tech':
            show_in_tech = stat.value
    out_file.statements.append(template(zone, potential, zone_unlock, show_in_tech))


def template_can_build_district(name:str, potential:BlockNode, allow:BlockNode):
    template_code = r"""
bca_can_build_district = {
    AND = {$potential$}
    AND = {$allow$}
}
"""
    template_ast = parse(template_code)
    obj:ObjectNode = template_ast.statements[0]  # 获取根对象
    obj.name.macro_expression = None
    obj.name.identifier = IdentifierNode(f"bca_can_build_{name}")

    def replace_macro(node:ASTNode, parent:ASTNode):
        for c in utils.astnode_children(node):
            replace_macro(c, node)
        if isinstance(node, IdentifierExpressionNode):
            if not node.macro_expression: return
            param_name = node.macro_expression.macro_params[0].name
            if param_name == "potential":
                if potential is None:
                    remove_from_block(parent)
                    return
                parent.statements = potential.statements
            elif param_name == "allow":
                if allow is None:
                    remove_from_block(parent)
                    return
                parent.statements = allow.statements

    replace_macro(obj, None)
    return obj

always_uncapped_districts = []

def template_is_uncapped(name:str, is_uncapped:BlockNode):
    template_code = r"""
bca_is_uncapped = {
    always = yes
}
"""
    template_ast = parse(template_code)
    obj:ObjectNode = template_ast.statements[0]  # 获取根对象
    obj.name.macro_expression = None
    obj.name.identifier = IdentifierNode(f"bca_is_uncapped_{name}")

    if is_uncapped:
        obj.body = is_uncapped

    return obj

for name, districts in ast['common/districts'].items():
    potential = None
    allow = None
    is_uncapped = None
    for stat in districts.body.statements:
        if not isinstance(stat, PropertyNode): continue
        if str(stat.key) == 'potential':
            potential = stat.value
        elif str(stat.key) == 'allow':
            allow = stat.value
        elif str(stat.key) == 'is_uncapped':
            is_uncapped = stat.value
    if not is_uncapped:
        always_uncapped_districts.append(name)
    out_file.statements.append(template_is_uncapped(name, is_uncapped))
    out_file.statements.append(template_can_build_district(name, potential, allow))

def zone_type_template(name:str):
    template_code = r"""
bca_primary_district_can_build_$NAME$ = {
    bca_can_build_zone = yes
    OR = {
        has_district = xx
        always = no
    }
}
"""
    template_ast = parse(template_code)
    obj:ObjectNode = template_ast.statements[0]  # 获取根对象
    obj.name.macro_expression = None
    obj.name.identifier = IdentifierNode(f"bca_primary_district_can_build_{name}")
    pre_condition_node:PropertyNode = obj.body.statements[0]
    pre_condition_node.key.identifier = IdentifierNode(f"bca_can_build_{name}")
    or_node:ConditionNode = obj.body.statements[1]
    temp:PropertyNode = or_node.body.statements[0]
    false_statement:PropertyNode = or_node.body.statements[1]
    statements = or_node.body.statements
    statements.clear()
    districts = zone_district_mapping.get(name, [])
    for district in districts:
        district_type = district_type_mapping.get(district)
        if district_type == "multi_zone":
            temp_copy = copy.copy(temp)
            temp_copy.value = IdentifierExpressionNode()
            temp_copy.value.identifier = IdentifierNode(district)
            statements.append(temp_copy)
    if len(statements) == 0:
        obj.body.statements.clear()
        obj.body.statements.append(false_statement)
    return obj

def zone_type_template_1(name:str):
    template_code = r"""
bca_secondary_district_can_build_$NAME$ = {
    bca_can_build_zone = yes
    OR = {
        bca_can_build_dst = yes
        always = no
    }
}
"""
    template_ast = parse(template_code)
    obj:ObjectNode = template_ast.statements[0]  # 获取根对象
    obj.name.macro_expression = None
    obj.name.identifier = IdentifierNode(f"bca_secondary_district_can_build_{name}")
    pre_condition_node:PropertyNode = obj.body.statements[0]
    pre_condition_node.key.identifier = IdentifierNode(f"bca_can_build_{name}")
    or_node:ConditionNode = obj.body.statements[1]
    temp:PropertyNode = or_node.body.statements[0]
    false_statement:PropertyNode = or_node.body.statements[1]
    statements = or_node.body.statements
    statements.clear()
    districts = zone_district_mapping.get(name, [])
    for district in districts:
        district_type = district_type_mapping.get(district)
        if district_type == "single_zone":
            temp_copy = copy.copy(temp)
            temp_copy.key = IdentifierExpressionNode()
            temp_copy.key.identifier = IdentifierNode(f'bca_can_build_{district}')
            statements.append(temp_copy)
    if len(statements) == 0:
        obj.body.statements.clear()
        obj.body.statements.append(false_statement)
    return obj

for name in zone_district_mapping.keys():
    out_file.statements.append(zone_type_template(name))
    out_file.statements.append(zone_type_template_1(name))

compile_to_file(out_file, "../common/scripted_triggers/zone_build_conditions.txt")

used_districts_set = set()
for zone, districts in zone_district_mapping.items():
    used_districts_set.update(districts)

used_districts_set_list = []
for name, district in ast['common/districts'].items():
    if name in used_districts_set:
        used_districts_set_list.append(name)
used_primary_districts_set_list = [name for name in used_districts_set_list if district_type_mapping.get(name) == "multi_zone" ]
used_secondary_districts_set_list = [name for name in used_districts_set_list if district_type_mapping.get(name) == "single_zone" ]

# output district list as yaml
import yaml

with open("./used_districts.yaml", "w", encoding="utf-8") as f:
    yaml.dump({"all_districts": used_districts_set_list}, f, allow_unicode=True)
    yaml.dump({"primary_districts": used_primary_districts_set_list}, f, allow_unicode=True)
    yaml.dump({"secondary_districts": used_secondary_districts_set_list}, f, allow_unicode=True)

# district -> List[zone]
zones_on_district:Dict[str, List[str]] = {}

for zone, districts in zone_district_mapping.items():
    for district in districts:
        zones_on_district.setdefault(district, []).append(zone)

with open("./zones_on_district.yaml", "w", encoding="utf-8") as f:
    yaml.dump(zones_on_district, f, allow_unicode=True)

with open("./districts_for_zone.yaml", "w", encoding="utf-8") as f:
    yaml.dump({"districts_for_zone": zone_district_mapping}, f, allow_unicode=True)

# load manual_config/used_secondary_districts.yaml
with open("./manual_config/used_secondary_districts.yaml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)
    used_secondary_districts = data.get("secondary_districts", [])

zone_district_mapping_single = {zone: [d for d in districts if district_type_mapping.get(d) == "single_zone" and d in used_secondary_districts] for zone, districts in zone_district_mapping.items()}
#remove empty entries
zone_district_mapping_single = {zone: districts for zone, districts in zone_district_mapping_single.items() if len(districts) > 0}
with open("./secondary_districts_for_zone.yaml", "w", encoding="utf-8") as f:
    yaml.dump({"secondary_districts_for_zone": zone_district_mapping_single}, f, allow_unicode=True)

zone_district_mapping_multi = {zone: [d for d in districts if district_type_mapping.get(d) == "multi_zone"] for zone, districts in zone_district_mapping.items()}
#remove empty entries
zone_district_mapping_multi = {zone: districts for zone, districts in zone_district_mapping_multi.items() if len(districts) > 0}
with open("./primary_districts_for_zone.yaml", "w", encoding="utf-8") as f:
    yaml.dump({"primary_districts_for_zone": zone_district_mapping_multi}, f, allow_unicode=True)

# overlapping_zone of zone_district_mapping_single and zone_district_mapping_multi
overlapping_zone = set(zone_district_mapping_single.keys()) & set(zone_district_mapping_multi.keys())
with open("./overlapping_zones.yaml", "w", encoding="utf-8") as f:
    yaml.dump({"overlapping_zones": list(overlapping_zone)}, f, allow_unicode=True)


zone_icon_list = []
for name, zone in ast['common/zones'].items():
    icon = None
    for stat in zone.body.statements:
        if not isinstance(stat, PropertyNode): continue
        if str(stat.key) == 'icon':
            icon = stat.value

    icon = str(icon) if icon else None
    # icon may with "", remove them
    if icon and icon.startswith('"') and icon.endswith('"'):
        icon = icon[1:-1]
    zone_icon_list.append({"id": name, "icon": icon if icon else ""})

with open("./zone_icon_list.yaml", "w", encoding="utf-8") as f:
    yaml.dump({"zone_icon_list": zone_icon_list}, f, allow_unicode=True)


with open("./always_uncapped_districts.yaml", "w", encoding="utf-8") as f:
    yaml.dump({"always_uncapped_districts": always_uncapped_districts}, f, allow_unicode=True)