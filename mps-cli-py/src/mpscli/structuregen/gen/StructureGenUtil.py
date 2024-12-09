def get_and_resolve_reference(snode, reference_name, repo):
    reference = snode.get_reference(reference_name)
    if reference is None:
        return None
    resolved_node = reference.resolve(repo)
    if resolved_node is None:
        snode_name = snode.get_property("name")
        print(f"Error: Could not resolve node reference '{reference_name}' for node with name {snode_name} in repo {repo}")
    return resolved_node


def get_concept_fqn(snode, snode_to_model_map):
    model = snode_to_model_map.get(snode)
    name = snode.get_property("name")
    if model is None:
        print(f"Error: Cannot find model for snode with name {name}")
        module_part = ""
    else:
        module_part = model.name + "."
    return module_part + name
