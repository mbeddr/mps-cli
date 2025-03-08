from jinja2 import Template


def get_class_template(concept_declaration_snode):
    template = Template(
        '''from typing import Optional, List, TYPE_CHECKING       
{% for my_import in concept_declaration_snode.get_imports() -%}
from {{ my_import[0] }}.{{ my_import[1] }} import {{ my_import[1] }}
{% endfor %}
{% if concept_declaration_snode.get_imports_for_type_checking() %}
if TYPE_CHECKING:
{%- for my_import in concept_declaration_snode.get_imports_for_type_checking() %}
    from {{ my_import[0] }}.{{ my_import[1] }} import {{ my_import[1] }}
{%- endfor %}
{% endif %}
class {{ concept_declaration_snode.get_class_name() }}({{ concept_declaration_snode.get_base_classes_names() }}):
    {% if concept_declaration_snode.has_no_content() %}
    pass
    {% endif %}
    {% if concept_declaration_snode.create_concept_methods() %}
    def can_be_root(self) -> bool:
        return {{ concept_declaration_snode.can_be_root() }}
    
    def alias(self) -> str:
        return "{{ concept_declaration_snode.get_alias() }}"
    
    def short_description(self) -> str:
        return "{{ concept_declaration_snode.get_short_description() }}"
    {% endif %}
    {% for property in concept_declaration_snode.get_properties() %}
    def {{ property[3] }}(self) -> Optional[{{ property[1] }}]:
      {%- if property[2] %}
      value = self.get_property("{{ property[0] }}")
      index = value.rfind('/')
      if index == -1:
          return None
      return {{ property[1] }}(value[index + 1:])
      {% else %}
      return self.get_property("{{ property[0] }}")
      {% endif %}
    {% endfor -%}
    {% for child in concept_declaration_snode.get_children_and_references() %}
    {%- if child[2] %}
    def {{ child[3] }}(self) {% if child[1] %}-> List["{{ child[1] }}"]{% endif %}:
          return self.get_children("{{ child[0] }}")
    {% else %}
    def {{ child[3] }}(self) {% if child[1] %}-> Optional["{{ child[1] }}"]{% endif %}:
          my_children = self.get_children("{{ child[0] }}")
          if my_children is None:
            return self.get_reference("{{ child[0] }}").resolve(self.repo)
          return my_children[0]
    {% endif %}
    {%- endfor -%}
''')
    rendered_template = template.render(concept_declaration_snode=concept_declaration_snode)
    return rendered_template


def get_impl_class_template(concept_declaration_snode):
    template_impl = Template('''
from {{ concept_declaration_snode.get_impl_import()[0] }}.{{concept_declaration_snode.get_impl_import()[1]}} import {{concept_declaration_snode.get_impl_import()[1]}}

class {{ concept_declaration_snode.get_class_name() }}Impl({{ concept_declaration_snode.get_class_name() }}):
    
    @staticmethod
    def get_concept_fqn():
        return "{{ concept_declaration_snode.get_snode_concept_fqn() }}"
    '''
                             )
    rendered_impl_template = template_impl.render(concept_declaration_snode=concept_declaration_snode)
    return rendered_impl_template


def get_enum_class_template(enum_declaration_snode):
    template_enum = Template('''
from enum import Enum

class {{ enum_declaration_snode.get_class_name() }}(Enum):
{% for member in enum_declaration_snode.get_members() %}
    {{ member[0] }} = "{{ member[1] }}"
    {%- endfor %}
    
    def get_presentation(self) -> str:
        return self.value
     ''')
    rendered_enum_template = template_enum.render(enum_declaration_snode=enum_declaration_snode)
    return rendered_enum_template
