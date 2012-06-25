import re

import simplejson as json
from django.core.exceptions import ValidationError
from django import forms
from django.forms.fields import Field, IntegerField, CharField, ChoiceField
from django.core.validators import RegexValidator

from nailgun.models import Cluster, Node, Recipe, Role, Release


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe

    def clean(self):
        return self.cleaned_data

    def clean_recipe(self):
        validate_recipe(self.cleaned_data['recipe'])
        return self.cleaned_data['recipe']


def validate_recipe(value):
    if not re.match(r'^[^\]]+::([^\]]+)@[0-9]+(\.[0-9]+){1,2}$', value):
        raise ValidationError('Recipe should be in a \
"cookbook::recipe@version" format')


def validate_role_recipes(value):
    if value and isinstance(value, list):
        map(validate_recipe, value)
        for i in value:
            try:
                rec_exist = Recipe.objects.get(recipe=i)
            except Recipe.DoesNotExist:
                raise ValidationError('Recipe %s does not exist' % i)
    else:
        raise ValidationError('Invalid recipe list')


validate_node_id = RegexValidator(regex=re.compile('^[\dA-F]{12}$'))


def validate_node_ids(value):
    if isinstance(value, list):
        for node_id in value:
            validate_node_id(node_id)
    else:
        raise ValidationError('Node list must be a list of node IDs')


class RoleForm(forms.ModelForm):
    recipes = Field(validators=[validate_role_recipes])

    class Meta:
        model = Role


class RoleFilterForm(forms.Form):
    node_id = Field(required=False, validators=[validate_node_id])


class ClusterForm(forms.Form):
    name = CharField(max_length=100, required=False)
    nodes = Field(required=False, validators=[validate_node_ids])


class ClusterCreationForm(forms.ModelForm):
    nodes = Field(required=False, validators=[validate_node_ids])

    class Meta:
        model = Cluster


def validate_node_metadata(value):
    if value is not None:
        if isinstance(value, dict):
            for field in ('block_device', 'interfaces', 'cpu', 'memory'):
                # TODO(mihgen): We need more comprehensive checks here
                # For example, now, it's possible to store value[field] = []
                if not field in value or value[field] == "":
                    raise ValidationError("Node metadata '%s' \
                            field is required" % field)
        else:
            raise ValidationError('Node metadata must be a dictionary')


def validate_node_roles(value):
    if not isinstance(value, list) or \
        not all(map(lambda i: isinstance(i, int), value)):
            raise ValidationError('Role list must be a list of integers')


def validate_release_node_roles(data):
    if not data or not isinstance(data, list):
        raise ValidationError('Invalid roles list')
    if not all(map(lambda i: 'name' in i, data)):
        raise ValidationError('Role name is empty')
    for role in data:
        if 'recipes' not in role or not role['recipes']:
            raise ValidationError('Recipes list for role "%s" \
should not be empty' % role['name'])
        for recipe in role['recipes']:
            validate_recipe(recipe)
            try:
                rec_exists = Recipe.objects.get(recipe=recipe)
            except Recipe.DoesNotExist:
                raise ValidationError('Recipe %s doesn\'t exist' % recipe)


class NodeForm(forms.Form):
    metadata = Field(required=False, validators=[validate_node_metadata])
    status = ChoiceField(required=False, choices=Node.NODE_STATUSES)
    name = CharField(max_length=100, required=False)
    fqdn = CharField(max_length=255, required=False)
    ip = CharField(max_length=15, required=False)
    mac = CharField(max_length=17, required=False)
    roles = Field(required=False, validators=[validate_node_roles])


class NodeCreationForm(NodeForm):
    id = CharField(validators=[validate_node_id])


class NodeFilterForm(forms.Form):
    cluster_id = IntegerField(required=False)


class ReleaseCreationForm(forms.ModelForm):
    roles = Field(validators=[validate_release_node_roles])

    class Meta:
        model = Release

    def clean(self):
        return self.cleaned_data
