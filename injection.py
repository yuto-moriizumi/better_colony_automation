import os
import re
from typing import List, Tuple, Optional

os.environ['STELLARIS_COMMON_ROOT'] = r'D:/SteamLibrary/steamapps/common/Stellaris/common'

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
		# Skip whitespace
		while i < len(content) and content[i].isspace():
			i += 1
		if i >= len(content):
			break
		
		# Check if we're at a multi-object list [obj1 obj2 ...]
		objects = []
		if content[i] == '[':
			# Find matching ]
			bracket_open = i
			j = i + 1
			while j < len(content) and content[j] != ']':
				j += 1
			if j >= len(content):
				# Malformed, skip
				i += 1
				continue
			# Extract list content, handling multiple lines
			list_content = content[bracket_open + 1:j]
			# Split by whitespace to get objects
			objects = list_content.split()
			i = j + 1  # Skip past ]
		else:
			# Single object - read until . or =
			obj_start = i
			while i < len(content) and content[i] not in '.=\n':
				i += 1
			single_obj = content[obj_start:i].strip()
			if single_obj:
				objects = [single_obj]
		
		if not objects:
			continue
		
		# Skip whitespace and optional dot
		while i < len(content) and content[i].isspace():
			i += 1
		if i < len(content) and content[i] == '.':
			i += 1
		
		# Parse property path until =
		path_start = i
		while i < len(content) and content[i] != '=':
			i += 1
		if i >= len(content):
			break
		property_path = content[path_start:i].strip()
		
		# Skip = and spaces
		i += 1
		while i < len(content) and content[i].isspace():
			i += 1
		
		# Determine operation
		op = "override"
		if content.startswith("append", i):
			op = "append"
			i += len("append")
		elif content.startswith("override", i):
			op = "override"
			i += len("override")
		elif content.startswith("wrap", i):
			op = "wrap"
			i += len("wrap")
		
		# Skip spaces to opening brace
		while i < len(content) and content[i].isspace():
			i += 1
		if i >= len(content) or content[i] != '{':
			continue
		
		# Find matching brace
		brace_open = i
		brace_close = find_matching_brace(content, i)
		if brace_close == -1:
			break
		body = content[brace_open + 1:brace_close]
		i = brace_close + 1
		
		# Create directives for each object
		for obj in objects:
			obj = obj.strip()
			if obj:
				path = [obj] + [p.strip() for p in property_path.split('.') if p.strip()]
				directives.append(InjectionDirective(path, op, body))
	
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


def apply_wrap(text: str, prop_open: int, prop_close: int, template: str, newline: str, indent_unit: str) -> str:
	# Wrap existing content with template containing [wrapped] placeholder
	# Extract original content
	original_content = text[prop_open + 1:prop_close]
	
	# Determine indentation context
	line_start = text.rfind('\n', 0, prop_open)
	if line_start == -1:
		line_start = 0
	else:
		line_start += 1
	leading_ws = re.match(r"\s*", text[line_start:prop_open]).group(0)
	inner_indent = leading_ws + indent_unit
	
	# Process template and replace [wrapped] with original content
	template_lines = template.splitlines()
	result_lines = []
	
	for line in template_lines:
		stripped = line.strip()
		if '[wrapped]' in stripped:
			# Replace [wrapped] with original content
			# Preserve indentation of [wrapped] line for the inserted content
			wrapped_indent_match = re.match(r'(\s*)\[wrapped\]', line)
			if wrapped_indent_match:
				wrapped_line_indent = wrapped_indent_match.group(1)
				# Insert original content directly, preserving its structure
				for orig_line in original_content.splitlines():
					# Keep original line as-is, will be re-indented by indent_body
					result_lines.append(wrapped_line_indent + orig_line.strip() if orig_line.strip() else orig_line)
		else:
			result_lines.append(line)
	
	# Join template without applying base indentation yet
	wrapped_body = newline.join(result_lines)
	
	# Now apply proper indentation to the entire wrapped structure
	# But first need to handle original content's relative indentation
	# Extract original lines and dedent them uniformly
	orig_lines = original_content.splitlines()
	orig_non_empty = [l for l in orig_lines if l.strip()]
	if orig_non_empty:
		min_indent = min(len(re.match(r'\s*', l).group(0)) for l in orig_non_empty)
		dedented_orig = [l[min_indent:] if len(l) > min_indent and l.strip() else l for l in orig_lines]
	else:
		dedented_orig = orig_lines
	
	# Rebuild template with dedented original content
	result_lines_final = []
	for line in template_lines:
		if '[wrapped]' in line.strip():
			wrapped_indent_match = re.match(r'(\s*)\[wrapped\]', line)
			if wrapped_indent_match:
				wrapped_line_indent = wrapped_indent_match.group(1)
				for orig_line in dedented_orig:
					if orig_line.strip():
						result_lines_final.append(wrapped_line_indent + orig_line)
					else:
						result_lines_final.append('')
		else:
			result_lines_final.append(line)
	
	wrapped_body = newline.join(result_lines_final)
	injected = indent_body(wrapped_body, newline, inner_indent)
	
	# Capture closing brace indentation
	close_line_start = text.rfind('\n', 0, prop_close)
	if close_line_start == -1:
		close_line_start = 0
	else:
		close_line_start += 1
	closing_indent = re.match(r"\s*", text[close_line_start:prop_close]).group(0)
	
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
	# Support multi-level path: top.level1.level2.level3...
	if not directive.target_path:
		return text
	
	# Find top-level object
	top = directive.target_path[0]
	found = find_top_object(text, top)
	if not found:
		return text  # Not found in this file
	
	_, current_open, current_close = found
	
	# Navigate through nested path (skip first element which is top)
	for i in range(1, len(directive.target_path)):
		key = directive.target_path[i]
		subblk = find_sub_block(text, current_open, current_close, key)
		
		if subblk:
			# Found the sub-block, continue deeper
			_, current_open, current_close = subblk
		else:
			# Sub-block not found
			if i == len(directive.target_path) - 1:
				# This is the final key - create it with the body
				text, _ = add_new_property(text, current_open, current_close, key, directive.body, newline, indent_unit)
				return text
			else:
				# Intermediate key missing - cannot proceed deeper
				# For now, skip this directive
				return text
	
	# Reached the target block - apply the operation
	if directive.operation == "append":
		return apply_append(text, current_open, current_close, directive.body, newline, indent_unit)
	elif directive.operation == "wrap":
		return apply_wrap(text, current_open, current_close, directive.body, newline, indent_unit)
	else:
		return apply_override(text, current_open, current_close, directive.body, newline, indent_unit)


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


def build_output_path(src: str, source_root: str, output_root: str, prefix: str, suffix: str) -> str:
	rel = os.path.relpath(src, source_root)
	rel_dir, filename = os.path.split(rel)
	base, ext = os.path.splitext(filename)
	new_name = f"{prefix}{base}{suffix}{ext}"
	return os.path.join(output_root, rel_dir, new_name)


def group_directives_by_top(directives: List[InjectionDirective]) -> dict:
	groups: dict = {}
	for d in directives:
		if not d.target_path:
			continue
		top = d.target_path[0]
		groups.setdefault(top, []).append(d)
	return groups


def apply_directives_to_files(source_dir: str, common_dir: str, directives: List[InjectionDirective], output_prefix: str, output_suffix: str) -> None:
	if not directives:
		return
	
	# Group directives by source file to avoid re-reading and overwriting
	files_to_process = {}  # {source_file_path: [directives]}
	
	# For each directive, find its source file and collect all directives for that file
	for directive in directives:
		if not directive.target_path:
			continue
		top = directive.target_path[0]
		source_files = find_source_files_for_top(source_dir, top)
		if not source_files:
			continue
		for src in source_files:
			if src not in files_to_process:
				files_to_process[src] = []
			files_to_process[src].append(directive)
	
	# Process each source file once, applying all its directives
	for src, directives_for_file in files_to_process.items():
		text = read_text(src)
		newline = detect_newline(text)
		indent_unit = detect_indentation_unit(text)

		# Group directives by top-level object
		top_to_directives = {}
		for d in directives_for_file:
			if not d.target_path:
				continue
			top = d.target_path[0]
			top_to_directives.setdefault(top, []).append(d)

		modified_blocks = []  # [(start_idx, block_text)]
		for top, ds in top_to_directives.items():
			found = find_top_object(text, top)
			if not found:
				continue
			name_idx, _, brace_close = found
			block_text = text[name_idx:brace_close + 1]
			updated_block = block_text
			for d in ds:
				updated_block = apply_one_directive(updated_block, d, newline, indent_unit)
			modified_blocks.append((name_idx, updated_block))

		if not modified_blocks:
			continue

		modified_blocks.sort(key=lambda x: x[0])
		out_text = (newline * 2).join(block for _, block in modified_blocks) + newline

		out_path = build_output_path(src, source_dir, common_dir, output_prefix, output_suffix)
		write_text(out_path, out_text)


def main():
	workspace_root = os.path.dirname(os.path.abspath(__file__))
	injection_root = os.path.join(workspace_root, "code_injection")
	common_root = os.path.join(workspace_root, "common")

	# Configure source scripts and output naming
	# source_root should point to the game's common folder, e.g. ".../Stellaris/common"
	source_root = os.environ.get("STELLARIS_COMMON_ROOT")
	output_prefix = os.environ.get("INJECTION_OUTPUT_PREFIX", "99_")
	output_suffix = os.environ.get("INJECTION_OUTPUT_SUFFIX", "_override")

	if not source_root:
		print("Missing STELLARIS_COMMON_ROOT. Set it to the game's common folder.")
		return

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
		v_dir = os.path.join(source_root, cat)
		c_dir = os.path.join(common_root, cat)
		directives = load_directives_for_category(inj_dir)
		apply_directives_to_files(v_dir, c_dir, directives, output_prefix, output_suffix)
		print(f"Applied {len(directives)} directives to category '{cat}'.")


if __name__ == "__main__":
	main()

