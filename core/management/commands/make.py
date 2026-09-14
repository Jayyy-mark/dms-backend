# core/management/commands/make.py
import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings

def to_snake_case(name):
    """
    Convert CamelCase to snake_case
    Example: RankRepository -> rank_repository
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()

class Command(BaseCommand):
    help = 'Global Artisan-style make command for any app: model, controller, repository'

    def add_arguments(self, parser):
        parser.add_argument('type', type=str, choices=['model','controller','repository'],
                            help='Type of file to create')
        parser.add_argument('name', type=str, help='Class name to create')
        parser.add_argument('--app', type=str, required=True, help='Target Django app name (dotted path like features.ranks)')

    def handle(self, *args, **options):
        type_ = options['type']
        name = options['name']
        app_name = options['app']

        # Convert dotted app path to folder path
        app_dir = os.path.join(settings.BASE_DIR, *app_name.split('.'))
        if not os.path.exists(app_dir):
            self.stdout.write(self.style.ERROR(f"App folder '{app_dir}' does not exist! Check your --app argument."))
            return

        # Map type to folder
        folder_map = {
            'model': 'models',
            'controller': os.path.join('presentation', 'controllers'),
            'repository': os.path.join('infrastructure', 'repositories')
        }
        folder = os.path.join(app_dir, folder_map[type_])
        os.makedirs(folder, exist_ok=True)

        # Determine filename
        filename = to_snake_case(name)
        if type_ == 'controller':
            filename += '_controller'
        elif type_ == 'repository':
            filename += '_repository'
        # models keep simple snake_case

        file_path = os.path.join(folder, f"{filename}.py")

        # Prevent overwrite
        if os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f"{type_.capitalize()} '{name}' already exists in app '{app_name}'!"))
            return

        # Templates
        if type_ == 'model':
            content = f"""from django.db import models
from django.utils import timezone

class {name}(models.Model):
    # TODO: Add your fields here
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
"""

        elif type_ == 'controller':
            content = f"""from django.shortcuts import render
from django.views import View

class {name}(View):
    # TODO: Add your view methods here
    pass
"""

        elif type_ == 'repository':
            content = f"""# Repository for {name}
from app.backend.features.{name.lower()}s.domain.{name.lower()}_entity import {name}Entity
from app.backend.features.{name.lower()}s.infrastructure.{name.lower()}_mapper import {name}Mapper
from features.{name.lower()}s.models import {name}
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ValidationError

class {name.lower()}Repository:
    def __init__(self, model : {name}, mapper : {name}Mapper):
        self.model = model
        self.mapper = mapper

    def all(self)->list[{name}Entity]:
        {name.lower()}s = self.model.objects.all()
        return [
            self.mapper.toEntity({name.lower()})
            for {name.lower()} in {name.lower()}s
        ]
    
    def get_by_id(self, {name.lower()}_id: int)->{name}Entity:
        try:
            {name.lower()} = self.model.objects.get(id={name.lower()}_id)
        except self.model.DoesNotExist:
            return None
        
        return self.mapper.toEntity({name.lower()})

    def create(self, entity : {name}Entity)->{name}Entity:
        modelData = self.mapper.toModel(entity)

        try:
             {name.lower()} = self.model.objects.create(**modelData)

        except IntegrityError as e:
            # unique constraint, FK error, etc.
            raise Exception(f"Database integrity error: ",str(e))

        except ValidationError as e:
            raise Exception(f"Validation error: ",e.message_dict)

        except DatabaseError as e:
            raise Exception(f"Database error: ",str(e))

        return self.mapper.toEntity({name.lower()})
    
    def update(self, entity: {name}Entity)->{name}Entity:
        
        try:
            {name.lower()} = self.model.objects.get(id=entity.id)
        except self.model.DoesNotExist:
            return None

        {name.lower()}.{name.lower()}_id = entity.{name.lower()}_id
        {name.lower()}.{name.lower()}_name = entity.{name.lower()}_name

        {name.lower()}.save()

        return self.mapper.toEntity({name.lower()})
    
    def delete(self, id: int)->bool:
        
        try:
            {name.lower()} = self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return False
        
        {name.lower()}.delete()

        return True
        
"""

        # Write file
        with open(file_path, 'w') as f:
            f.write(content)

        self.stdout.write(self.style.SUCCESS(f"{type_.capitalize()} '{name}' created at {file_path}"))
