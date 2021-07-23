{{ fullname | escape | underline}}

.. automodule:: {{ fullname }}

   {% block attributes %}
   {% if attributes %}
   .. rubric:: Module attributes

   .. autosummary::
      :toctree:
   {% for item in attributes %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block functions %}
   {% if functions %}
   .. rubric:: {{ _('Functions') }}

   .. autosummary::
      :toctree:
      :nosignatures:
   {% for item in functions %}
   .. autofunction:: {{ item }}

   .. _sphx_glr_backref_{{fullname}}.{{item}}:

   .. minigallery:: {{fullname}}.{{item}}
      :add-heading:

   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
      {% if classes %}
      {% for item in classes %}
       {% block examples %}
      {% if item=='MDE' or item=='HeliosFr' or item=='ForceAtlas2' %} 
         .. _sphx_glr_backref_helios.layouts.{{item}}:
         .. minigallery:: helios.layouts.{{item}}
            :add-heading:
      {% else %}
         .. _sphx_glr_backref_{{fullname}}.{{item}}:
         .. minigallery:: {{fullname}}.{{item}}
            :add-heading:
      {% endif %}
      {% endblock %}
      .. autoclass:: {{ item }}
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