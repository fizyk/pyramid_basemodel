# -*- coding: utf-8 -*-

"""Provides shared mixins for ORM classes."""

__all__ = [
    'PolymorphicBaseMixin',
    'PolymorphicMixin',
    'TouchMixin',
    'GetByAttrMixin,',
    'GetByIdMixin',
    'GetBySlugMixin',
    'GetByTitleMixin',
    'GetByNameMixin',
    'GetByEmailMixin',
    'ReprMixin',
]

import logging
logger = logging.getLogger(__name__)

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy.ext.declarative import declared_attr

from pyramid_basemodel import save as save_to_db

class PolymorphicBaseMixin(object):
    """Provides a dynamically generated ``__mapper_args__`` property for
      [single table inherited][] ORM classes::
      
      [single table inherited]: http://bit.ly/TBDmMx
    """
    
    discriminator = Column(u'type', Unicode(16))
    
    @declared_attr
    def __mapper_args__(self):
        """Set the ``polymorphic_identity`` value to the lower case class name."""
        
        return {
            'polymorphic_on': self.discriminator,
            'polymorphic_identity': self.__class__.__name__.lower()
        }
    

class PolymorphicMixin(object):
    """Provides a dynamically generated ``__mapper_args__`` property for
      [single table inherited][] ORM classes::
      
      [single table inherited]: http://bit.ly/TBDmMx
    """
    
    @declared_attr
    def __mapper_args__(self):
        """Set the ``polymorphic_identity`` value to the lower case class name."""
        
        return {'polymorphic_identity': self.__class__.__name__.lower()}


class TouchMixin(object):
    """Provides ``touch`` and ``propagate_touch`` methods."""
    
    def propagate_touch(self):
        """Override to propagate touch events to relations.
          
          Note that this event *should not* be  called in response to an
          SQLAlchemy ORM attribute modified event, as you can't reliably
          update relations in an attribute event handler.
        """
    
    def touch(self, propagate=True, now=None, save=None):
        """Update self.modified."""
        
        # Compose.
        if now is None:
            now = datetime.utcnow
        if save is None:
            save = save_to_db
        
        # Update self's modified date.
        self.modified = now()
        save(self)
        
        # Call propagate touch.
        if propagate:
            self.propagate_touch()


sentinel = object()


class GetByAttrMixin(object):
    """A mixin for adding ``by_attr`` helper to models."""

    def by_attr(cls, attr, value):
        """Get a Model object by one of its attributes.

        Return ``None`` if the object is not found.
        """

        return cls.query.filter(getattr(cls, attr)==value).first()

class GetByIdMixin(GetByAttrMixin):
    """A mixin for adding ``by_id`` helper to models."""

    @classmethod
    def by_id(cls, id, default=sentinel):
        """Get a Model object by its id.

        Return ``None`` if the object is not found.
        On error raise exception or return `default`, if it is set.
        """

        try:
            id = int(id)
            return cls.by_attr('id', id)
        except (ValueError, TypeError) as exc:
            if default == sentinel:
                raise exc
            else:
                return default


class GetBySlugMixin(GetByAttrMixin):
    """A mixin for adding ``by_slug`` helper to models."""

    @classmethod
    def by_slug(cls, slug, default=sentinel):
        """Get a Model object by its slug.

        Return ``None`` if the object is not found.
        On Unicode error raise exception or return `default`, if it is set.
        """

        try:
            str(slug).decode('ascii')
            return cls.by_attr('slug', slug)
        except UnicodeDecodeError as exc:
            if default == sentinel:
                raise exc
            else:
		return default


class GetByTitleMixin(GetByAttrMixin):
    """A mixin for adding ``by_title`` helper to models."""

    @classmethod
    def by_title(cls, title, default=sentinel):
        """Get a Model object by its title.

        Return ``None`` if the object is not found.
        On Unicode error raise exception or return `default`, if it is set.
        """

        try:
            str(title).decode('ascii')
            return cls.by_attr('title', title)
        except UnicodeDecodeError as exc:
            if default == sentinel:
                raise exc
            else:
                return default


class GetByNameMixin(GetByAttrMixin):
    """A mixin for adding by_name method to models."""

    @classmethod
    def by_name(cls, name):
        """Get a Model object by name.

        Return ``None`` if the object is not found.
        """

        return cls.by_attr('name', name)


class GetByEmailMixin(GetByAttrMixin):
    """A mixin for adding ``by_email`` helper to models."""

    @classmethod
    def by_email(cls, email):
        """Get a Model object by its email.

        Return ``None`` if the object is not found.
        """

        return cls.by_attr('email', email)


class ReprMixin(object):
    """Provides a generic ``__repr__`` implementation."""

    def __repr__(self):
        """Return a generic string representation of a class.

        The following format is used: '<class_name:id (field=value...)>.
        Only name, title, slug, email fields are included in the string.
        """

        cls = type(self)
        fields = ['name', 'title', 'slug', 'email']
        formatted_fields = []
        class_name = cls.__name__
        id = cls.__dict__.get('id', None)

        for field_name in fields:
            try:
                field_value = cls.__dict__[field_name]
            except KeyError:
                continue
            if field_value:
                field_value = field_value.encode('utf-8')
            formatted_fields.append('{}={}, '.format(field_name, field_value))
        concat_fields = ''.join(formatted_fields)[:-2]

        return '<{}:{} ({})>'.format(class_name, id, concat_fields)
