{{ fullname | escape | underline}}


.. automodule:: {{ fullname }}

   {% block table %}
   {% if classes %}
   
   List of Objects
   ---------------
   {% for objname in classes %}
      `{{objname}},  <#{{fullname}}.{{objname}}>`_

   {%- endfor %}
   {% endif %}
   {% if functions %}
   List of Functions
   -----------------
   {% for function in functions %}
      `{{function}},  <#{{fullname}}.{{function}}>`_
   {%- endfor %}
   {% endif %}
   {% endblock %}
   {% block functions %}
   {% if functions %}

   .. autosummary::
      :toctree:
      :nosignatures:
   {% for item in functions %}
   {% set vars = {'under':''} %}
   {% for stuff in range(item|length) %}
      {% if vars.update({'under': '-'+vars['under']}) %} {% endif %}
   {%- endfor %}
   {{ item }}
   {{vars['under']}}
   .. autofunction:: {{ item }}

   .. _sphx_glr_backref_{{fullname}}.{{item}}:

   .. minigallery:: {{fullname}}.{{item}}
      :add-heading:

   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
   {% if classes %}
   {% for objname in classes %}
   {% set vars = {'under':''} %}
   {% for stuff in range(objname|length) %}
      {% if vars.update({'under': '-'+vars['under']}) %} {% endif %}
   {%- endfor %}
   {{ objname }}
   {{vars['under']}}

   .. autoclass:: {{ objname }}
      :members:
      :show-inheritance:
      :inherited-members:
      :special-members: __call__, __add__, __mul__
      {% block methods %}
         {% if methods %}
         .. rubric:: {{ _('Methods') }}
         .. autosummary::
            :nosignatures:
         {% for item in methods %}
            {%- if not item.startswith('_') %}
            ~{{ name }}.{{ item }}
            {%- endif -%}
         {%- endfor %}
         {% endif %}
      {% endblock %}
      {% block attributes %}
         {% if attributes %}
         .. rubric:: {{ _('Class Attributes') }}
         .. autosummary::
         {% for item in attributes %}
            ~{{ name }}.{{ item }}
         {%- endfor %}
         {% endif %}
      {% endblock %}
      {% if objname=='MDE' or objname=='HeliosFr' or objname=='ForceAtlas2' %} 
      .. _sphx_glr_backref_helios.layouts.{{objname}}:
      .. minigallery:: helios.layouts.{{objname}}
         :add-heading:
      {% elif objname %}
      .. _sphx_glr_backref_{{fullname}}.{{objname}}:
      .. minigallery:: {{fullname}}.{{objname}}
         :add-heading:
      {% endif %}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block exceptions %}
   {% if exceptions %}
   .. rubric:: {{ _('Exceptions') }}

   .. autosummary::
      :toctree:
   {% for item in exceptions %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

{% block modules %}
{% if modules %}
.. autosummary::
   :toctree:
   :template: custom-module-template.rst
   :recursive:
{% for item in modules %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}