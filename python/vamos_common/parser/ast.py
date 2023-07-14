def visit_ast(node, lvl, fn, *args):
    fn(lvl, node, *args)
    if node is None:
        return

    if not hasattr(node, "children"):
        return
    for ch in node.children:
        visit_ast(ch, lvl + 1, fn, args)


def visit_ast_dfs(node, lvl, fn, *args):
    if node is None:
        return
    # if not hasattr(node, "children"):
    #    return

    for ch in node.children:
        visit_ast_dfs(ch, lvl + 1, fn, args)

    fn(lvl, node, *args)


def visit_dfs(ast, fn, *args):
    visit_ast_dfs(ast, 0, fn, *args)
