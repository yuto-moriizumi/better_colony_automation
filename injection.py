import os
import re
from typing import List, Tuple, Optional


class InjectionDirective:
	def __init__(self, target_path: List[str], operation: str, body: str):
		self.target_path = target_path  # e.g. ["building_research_lab_1", "destroy_trigger"]
		self.operation = operation  # "append" or "override"
		self.body = body  # content inside braces


def read_text(path: str) -> str:
	with open(path, "r", encoding="utf-8") as f:
		return f.read()


def write_text(path: str, content: str) -> None:
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		f.write(content)


def find_matching_brace(text: str, start_idx: int) -> int:
	"""Given text and index at '{', find matching '}' index. Returns index of '}' or -1"""
	depth = 0
	i = start_idx
	while i < len(text):
		ch = text[i]
		if ch == '{':
			depth += 1
		elif ch == '}':
			depth -= 1
			if depth == 0:
				return i
		i += 1
	return -1


def detect_newline(text: str) -> str:
	if "\r\n" in text:
		return "\r\n"
	return "\n"


def detect_indentation_unit(text: str) -> str:
	# Prefer tab if file uses tabs in indentation; else 4 spaces
	tab_count = text.count("\n\t")
	space_indent = re.findall(r"\n( +)\S", text)
	if tab_count > 0:
		return "\t"
	# choose most common space length
	if space_indent:
		lengths = {}
		for s in space_indent:
			lengths[len(s)] = lengths.get(len(s), 0) + 1
		common = max(lengths, key=lengths.get)
		return " " * min(common, 4)
	return "    "


def parse_injection_file(content: str) -> List[InjectionDirective]:
	directives: List[InjectionDirective] = []
	i = 0
	while i < len(content):
		# Find next '=' that starts a directive
		eq_idx = content.find('=', i)
		if eq_idx == -1:
			break
		# Extract key path left of '='
		# Go back to start of the line and strip spaces
		line_start = content.rfind('\n', 0, eq_idx)
		if line_start == -1:
			line_start = 0
		else:
			line_start += 1
		key_str = content[line_start:eq_idx].strip()
		# After '=', allow optional spaces and operation word
		j = eq_idx + 1
		while j < len(content) and content[j].isspace():
			j += 1
		op = "override"  # default behavior when not specified
		if content.startswith("append", j):
			op = "append"
			j += len("append")
		elif content.startswith("override", j):
			op = "override"
			j += len("override")
		# Skip spaces to the opening brace
		while j < len(content) and content[j].isspace():
			j += 1
		if j >= len(content) or content[j] != '{':
			# Not a block directive; skip this line
			i = eq_idx + 1
			continue
		body_start = j + 1
		body_end_brace = find_matching_brace(content, j)
		if body_end_brace == -1:
			# malformed; abort
			break
		body = content[body_start:body_end_brace]
		path = [p.strip() for p in key_str.split('.') if p.strip()]
		directives.append(InjectionDirective(path, op, body))
		i = body_end_brace + 1
	return directives


def find_top_object(text: str, name: str) -> Optional[Tuple[int, int, int]]:
	"""Find 'name = { ... }' block. Returns (name_idx, brace_open_idx, brace_close_idx) or None"""
	# Match word boundary, allowing spaces
	pattern = re.compile(r"\b" + re.escape(name) + r"\s*=\s*\{", re.MULTILINE)
	m = pattern.search(text)
	if not m:
		return None
	brace_open = m.end() - 1
	brace_close = find_matching_brace(text, brace_open)
	if brace_close == -1:
		return None
	return (m.start(), brace_open, brace_close)


def find_sub_block(text: str, obj_open: int, obj_close: int, key: str) -> Optional[Tuple[int, int, int]]:
	"""Within object [obj_open,obj_close], find 'key = { ... }'. Returns (key_idx, brace_open, brace_close)"""
	segment = text[obj_open:obj_close + 1]
	m = re.search(r"\b" + re.escape(key) + r"\s*=\s*\{", segment)
	if not m:
		return None
	abs_key_idx = obj_open + m.start()
	brace_open = obj_open + m.end() - 1
	brace_close = find_matching_brace(text, brace_open)
	if brace_close == -1 or brace_close > obj_close:
		return None
	return (abs_key_idx, brace_open, brace_close)


def indent_body(body: str, newline: str, indent: str) -> str:
	lines = body.splitlines()
	# Trim leading/trailing empty lines for cleaner injection
	while lines and lines[0].strip() == "":
		lines.pop(0)
	while lines and lines[-1].strip() == "":
		lines.pop()
	if not lines:
		return ""
	# Dedent uniformly by minimal leading whitespace to avoid double-indenting
	def leading_ws_len(s: str) -> int:
		return len(re.match(r"\s*", s).group(0))
	non_empty = [l for l in lines if l.strip() != ""]
	min_lead = min((leading_ws_len(l) for l in non_empty), default=0)
	dedented = [l[min_lead:] if l.strip() != "" else l for l in lines]
	return newline.join((indent + l) if l.strip() != "" else l for l in dedented)


def apply_append(text: str, prop_open: int, prop_close: int, body: str, newline: str, indent_unit: str) -> str:
	# Determine current indentation of property content
	# Find start of the line where '{' appears
	line_start = text.rfind('\n', 0, prop_open)
	if line_start == -1:
		line_start = 0
	else:
		line_start += 1
	leading_ws = re.match(r"\s*", text[line_start:prop_open]).group(0)
	inner_indent = leading_ws + indent_unit
	injected = indent_body(body, newline, inner_indent)
	
	# Capture closing brace indentation to preserve it
	close_line_start = text.rfind('\n', 0, prop_close)
	if close_line_start == -1:
		close_line_start = 0
	else:
		close_line_start += 1
	closing_indent = re.match(r"\s*", text[close_line_start:prop_close]).group(0)
	
	# Build insertion with proper indentation for closing brace
	if injected:
		insertion = newline + injected + newline + closing_indent
	else:
		insertion = ""
	
	# Insert just before the closing brace
	return text[:prop_close] + insertion + text[prop_close:]


def apply_override(text: str, prop_open: int, prop_close: int, body: str, newline: str, indent_unit: str) -> str:
	# Replace content between '{' and '}' with new body
	line_start = text.rfind('\n', 0, prop_open)
	if line_start == -1:
		line_start = 0
	else:
		line_start += 1
	leading_ws = re.match(r"\s*", text[line_start:prop_open]).group(0)
	inner_indent = leading_ws + indent_unit
	injected = indent_body(body, newline, inner_indent)
	
	# Capture closing brace indentation to preserve it
	close_line_start = text.rfind('\n', 0, prop_close)
	if close_line_start == -1:
		close_line_start = 0
	else:
		close_line_start += 1
	closing_indent = re.match(r"\s*", text[close_line_start:prop_close]).group(0)
	
	# Build replacement with proper indentation for closing brace
	if injected:
		replacement = newline + injected + newline + closing_indent
	else:
		replacement = ""
	
	return text[:prop_open + 1] + replacement + text[prop_close:]


def add_new_property(text: str, obj_open: int, obj_close: int, key: str, body: str, newline: str, indent_unit: str) -> Tuple[str, int]:
	# Insert before obj_close
	# Determine indentation of entries inside object
	line_start = text.rfind('\n', 0, obj_open)
	if line_start == -1:
		line_start = 0
	else:
		line_start += 1
	leading_ws = re.match(r"\s*", text[line_start:obj_open]).group(0)
	entry_indent = leading_ws + indent_unit
	inner_indent = entry_indent + indent_unit
	injected_body = indent_body(body, newline, inner_indent)
	block = (
		newline
		+ f"{entry_indent}{key} = {{" + newline
		+ (injected_body + newline if injected_body else "")
		+ f"{entry_indent}}}" + newline
	)
	new_text = text[:obj_close] + block + text[obj_close:]
	# obj_close shifts by len(block)
	return new_text, obj_close + len(block)


def apply_one_directive(text: str, directive: InjectionDirective, newline: str, indent_unit: str) -> str:
	# Currently support path of length 2: top.object_property
	if not directive.target_path:
		return text
	top = directive.target_path[0]
	sub = directive.target_path[1] if len(directive.target_path) > 1 else None
	found = find_top_object(text, top)
	if not found:
		return text  # Not found in this file
	_, obj_open, obj_close = found
	if sub is None:
		# If sub not provided, override whole object body (advanced use-case)
		if directive.operation == "append":
			# Append at end of object
			text, _ = add_new_property(text, obj_open, obj_close, "__injected__", directive.body, newline, indent_unit)
			return text
		else:
			# Replace entire object content between braces
			return apply_override(text, obj_open, obj_close, directive.body, newline, indent_unit)
	# Find sub block
	subblk = find_sub_block(text, obj_open, obj_close, sub)
	if subblk:
		_, prop_open, prop_close = subblk
		if directive.operation == "append":
			return apply_append(text, prop_open, prop_close, directive.body, newline, indent_unit)
		else:
			return apply_override(text, prop_open, prop_close, directive.body, newline, indent_unit)
	# Sub not found; create new property
	text, _ = add_new_property(text, obj_open, obj_close, sub, directive.body, newline, indent_unit)
	return text


def load_directives_for_category(category_dir: str) -> List[InjectionDirective]:
	directives: List[InjectionDirective] = []
	if not os.path.isdir(category_dir):
		return directives
	for root, _, files in os.walk(category_dir):
		for fn in files:
			if not fn.lower().endswith('.txt'):
				continue
			p = os.path.join(root, fn)
			content = read_text(p)
			directives.extend(parse_injection_file(content))
	return directives


def find_source_files_for_top(vanilla_category_dir: str, top_name: str) -> List[str]:
	matches: List[str] = []
	pattern = re.compile(r"\b" + re.escape(top_name) + r"\s*=\s*\{", re.MULTILINE)
	for root, _, files in os.walk(vanilla_category_dir):
		for fn in files:
			if not fn.lower().endswith('.txt'):
				continue
			p = os.path.join(root, fn)
			try:
				text = read_text(p)
			except Exception:
				continue
			if pattern.search(text):
				matches.append(p)
	return matches


def group_directives_by_top(directives: List[InjectionDirective]) -> dict:
	groups: dict = {}
	for d in directives:
		if not d.target_path:
			continue
		top = d.target_path[0]
		groups.setdefault(top, []).append(d)
	return groups


def apply_directives_to_files(vanilla_dir: str, common_dir: str, directives: List[InjectionDirective]) -> None:
	if not directives:
		return
	by_top = group_directives_by_top(directives)
	# For each top id, locate source file(s) and apply directives
	for top, dirs in by_top.items():
		source_files = find_source_files_for_top(vanilla_dir, top)
		if not source_files:
			# Not found; skip
			continue
		for src in source_files:
			text = read_text(src)
			newline = detect_newline(text)
			indent_unit = detect_indentation_unit(text)
			for d in dirs:
				text = apply_one_directive(text, d, newline, indent_unit)
			# Write to common path preserving relative
			rel = os.path.relpath(src, vanilla_dir)
			out_path = os.path.join(common_dir, rel)
			write_text(out_path, text)


def main():
	workspace_root = os.path.dirname(os.path.abspath(__file__))
	vanilla_root = os.path.join(workspace_root, "vanilla_file")
	injection_root = os.path.join(workspace_root, "code_injection")
	common_root = os.path.join(workspace_root, "common")

	categories = []
	# Mirror code_injection subfolders (e.g., buildings)
	if os.path.isdir(injection_root):
		for name in os.listdir(injection_root):
			cat_path = os.path.join(injection_root, name)
			if os.path.isdir(cat_path):
				categories.append(name)

	if not categories:
		print("No injection categories found under code_injection/")
		return

	for cat in categories:
		inj_dir = os.path.join(injection_root, cat)
		v_dir = os.path.join(vanilla_root, cat)
		c_dir = os.path.join(common_root, cat)
		directives = load_directives_for_category(inj_dir)
		apply_directives_to_files(v_dir, c_dir, directives)
		print(f"Applied {len(directives)} directives to category '{cat}'.")


if __name__ == "__main__":
	main()

