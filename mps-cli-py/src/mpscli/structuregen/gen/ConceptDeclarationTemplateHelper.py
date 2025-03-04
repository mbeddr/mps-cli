import logging

from mpscli.model.SNode import SNode
from mpscli.structuregen.gen.GenerationConstants import ENUM_DECLARATION_CONCEPT_NAME, CONCEPT_DECLARATION_CONCEPT_NAME, BASE_CONCEPT_FQN, INTERFACE_DECLARATION_CONCEPT_NAME
from mpscli.structuregen.gen.StructureGenUtil import get_and_resolve_reference, get_concept_fqn
from mpscli.structuregen.gen.StructureTemplates import get_class_template
from mpscli.structuregen.gen.StructureTemplates import get_impl_class_template


class AbstractDeclarationTemplateHelper:
    def __init__(self, snode, snode_to_model_map):
        self.snode = snode
        self.snode_to_model_map = snode_to_model_map

    def get_class_name(self):
        return self.snode.get_property("name")

    def get_concept_file_path(self):
        return self.get_snode_concept_fqn().replace(".", "/")

    def get_concept_folder_path(self):
        file_path = self.get_concept_file_path()
        last_slash_pos = file_path.rfind('/')
        folder_path = file_path[:last_slash_pos]
        return folder_path

    def get_snode_concept_fqn(self):
        return get_concept_fqn(self.snode, self.snode_to_model_map)


class AbstractConceptDeclarationTemplateHelper(AbstractDeclarationTemplateHelper):
    def __init__(self, snode, snode_to_model_map, repo):
        super().__init__(snode, snode_to_model_map)
        self.repo = repo

    def get_imports(self):
        imports = []
        for used_class in self.get_used_classes(False):
            imports.append((self.get_module_name(used_class), used_class.get_property("name")))
        if self.is_base_concept():
            imports.append(("mpscli.model.structure", "AbstractSNodeWithStructure"))
        if self.is_top_interface():
            imports.append(("mpscli.model.structure", "AbstractSNodeInterfaceWithStructure"))
        return imports

    def get_imports_for_type_checking(self):
        imports_for_type_checking = []
        for used_class_in_link in self.get_used_classes_in_links():
            imports_for_type_checking.append((self.get_module_name(used_class_in_link), used_class_in_link.get_property("name")))
        return imports_for_type_checking

    def is_base_concept(self):
        return get_concept_fqn(self.snode, self.snode_to_model_map) == BASE_CONCEPT_FQN

    def get_impl_import(self):
        return self.snode_to_model_map[self.snode].name, self.snode.get_property("name")

    def get_base_classes_names(self):
        names = [base_concept.get_property("name") for base_concept in [bc for bc in self.get_base_concept_and_implementing_interfaces() if bc is not None]]
        if self.is_base_concept():
            names.append("AbstractSNodeWithStructure")
        if self.is_top_interface():
            names.append("AbstractSNodeInterfaceWithStructure")
        return ', '.join(names)

    def get_used_classes(self, include_classes_in_links):
        used_classes = []
        used_classes.extend(self.get_base_concept_and_implementing_interfaces())
        for property_declaration in self.snode.get_children("propertyDeclaration"):
            data_type_declaration = property_declaration.get_reference("dataType").resolve(self.repo)
            if data_type_declaration is None:
                continue
            if data_type_declaration.concept.name == ENUM_DECLARATION_CONCEPT_NAME:
                used_classes.append(data_type_declaration)
        if include_classes_in_links:
            used_classes.extend(self.get_used_classes_in_links())
        none_elements = [uc for uc in used_classes if uc is None]
        if none_elements:
            logging.error(f"{len(none_elements)} none elements found during finding used classes of {self.get_class_name()}")
        return [uc for uc in used_classes if uc is not None]

    def get_used_classes_in_links(self):
        used_classes_in_links = []
        for links_declaration in self.snode.get_children("linkDeclaration"):
            target = get_and_resolve_reference(links_declaration, "target", self.repo)
            if target is not None:
                used_classes_in_links.append(target)
            else:
                logging.error(f"Error: cannot get target for link declaration {links_declaration}")
        return used_classes_in_links

    def get_properties(self):
        property_declarations = self.snode.get_children("propertyDeclaration")
        return tuple((property_declaration.get_property("name"), self.get_primitive_datatype(property_declaration), self.is_enum_declaration(property_declaration) ) for property_declaration in property_declarations)

    def get_children_and_references(self):
        links_declarations = self.snode.get_children("linkDeclaration")
        children_and_refs = []
        for links_declaration in links_declarations:
            role = links_declaration.get_property("role")
            target = get_and_resolve_reference(links_declaration, "target", self.repo)
            target_str = ""
            if target is not None:
                target_str = target.get_property("name")
            children_and_refs.append((role, target_str, self.is_many(links_declaration)))

        return children_and_refs

    def get_module_name(self, snode):
        if snode is None:
            logging.error("Error: cannot get module name for None snode.")
            return ""
        model = self.snode_to_model_map.get(snode)
        if model is None:
            snode_name = snode.get_property("name")
            logging.warning(f"Cannot find model for snode with name {snode_name}")
            return ""
        return model.name

    def get_base_concept_and_implementing_interfaces(self) -> list[SNode]:
        pass

    def create_concept_methods(self):
        pass

    def has_no_content(self):
        pass

    def generate_class(self):
        return get_class_template(self)

    def generate_class_impl(self):
        return get_impl_class_template(self)

    def is_enum_declaration(self, property_declaration) -> bool:
        datatype_declaration = get_and_resolve_reference(property_declaration, "dataType", self.repo)
        if datatype_declaration is None:
            return False
        return datatype_declaration.concept.name == ENUM_DECLARATION_CONCEPT_NAME

    def get_primitive_datatype(self, property_declaration):
        datatype_declaration = get_and_resolve_reference(property_declaration, "dataType", self.repo)
        if datatype_declaration is None:
            logging.error("Error: Cannot find dataType declaration for property declaration.")
            return "str"
        type_name = datatype_declaration.get_property("name")
        if type_name == "string":
            return "str"
        if type_name == "boolean":
            return "bool"
        if type_name == "integer":
            return "int"
        return type_name

    def can_be_root(self):
        can_be_root = self.snode.get_property("rootable")
        return "True" if can_be_root == "true" else "False"

    def get_alias(self):
        alias = self.snode.get_property("conceptAlias")
        return alias if alias is not None else ""

    def get_short_description(self):
        short_description = self.snode.get_property("conceptShortDescription")
        return short_description if short_description is not None else ""

    @staticmethod
    def is_many(links_declaration):
        cardinality = links_declaration.get_property("sourceCardinality")
        return cardinality and cardinality.endswith('n')

    def is_top_interface(self):
        return self.snode.concept.name == INTERFACE_DECLARATION_CONCEPT_NAME and len(self.get_base_concept_and_implementing_interfaces()) == 0


class ConceptDeclarationTemplateHelper(AbstractConceptDeclarationTemplateHelper):

    def get_base_concept_and_implementing_interfaces(self):
        base_classes = []
        super_concept = get_and_resolve_reference(self.snode, "extends", self.repo)
        if super_concept is None:
            snode_name = self.snode.get_property("name")
            if snode_name != "BaseConcept":
                logging.error(f"Info: Cannot find BaseConcept for concept {snode_name}")
        else:
            base_classes.append(super_concept)
        for implements_interface in self.snode.get_children("implements"):
            base_classes.append(get_and_resolve_reference(implements_interface, "intfc", self.repo))
        return [item for item in base_classes if item is not None]

    def create_concept_methods(self):
        return True

    def has_no_content(self):
        return False


class InterfaceDeclarationTemplateHelper(AbstractConceptDeclarationTemplateHelper):

    def get_base_concept_and_implementing_interfaces(self):
        children = [child for child in self.snode.get_children("extends") if child is not None]
        return [get_and_resolve_reference(implements_interface, "intfc", self.repo) for implements_interface in children]

    def create_concept_methods(self):
        return False

    def has_no_content(self):
        return not self.get_properties() and not self.get_children_and_references()


def create_helper_by_declaration_name(declaration_name, concept_to_generate, snode_to_model_map, repo) -> AbstractConceptDeclarationTemplateHelper:
    if declaration_name == CONCEPT_DECLARATION_CONCEPT_NAME:
        return ConceptDeclarationTemplateHelper(concept_to_generate, snode_to_model_map, repo)
    return InterfaceDeclarationTemplateHelper(concept_to_generate, snode_to_model_map, repo)
