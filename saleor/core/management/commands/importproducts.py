# -*- coding: utf-8 -*-
import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from saleor.product.models import Product, Category, ProductType, ProductVariant, ProductAttribute, AttributeChoiceValue


MAP_BOOLEANS = {'TRUE': True, 'FALSE': False}

class Command(BaseCommand):
    help = 'Import products from csv file'

    def handle(self, *args, **options):

        with open('{}/products.csv'.format(settings.PROJECT_ROOT), encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                pk = row['id']
                sku = row['sku']
                print('Trying to add product ({})'.format(sku))
                name = row['name']
                description = row['description']
                price = row['price']
                stock_quantity = row['stock']
                is_published = MAP_BOOLEANS[row['is_published']]

                category = row['category']
                product_type = row['type']

                variant_name = row['variant_name']
                variant_price = row['variant_price']

                attribute = slugify(row['attribute'])
                attribute_slug = slugify(attribute)
                attribute_value = row['attribute_value']
                attribute_value_slug = slugify(attribute_value)

                try:
                    product_var = ProductVariant.objects.get(sku=sku)
                except ProductVariant.DoesNotExist:
                    product_var = ProductVariant(sku=sku)
                except ProductVariant.MultipleObjectsReturned:
                    print('Revise sku ({}), multiple product variants returned'.format(sku))
                    continue

                product_var.quantity = stock_quantity

                try:
                    product = Product.objects.get(id=pk)
                except Product.DoesNotExist:
                    product = Product(id=pk)
                except Product.MultipleObjectsReturned:
                    print('Revise id ({}), multiple product variants returned'.format(pk))
                    continue

                try:
                    product_type = ProductType.objects.get(name=product_type)
                except ProductType.DoesNotExist:
                    print('Product type ({}) for product ({}) does not exist, creating...'.format(product_type, name))
                    product_type = ProductType.objects.create(name=product_type)

                product.product_type = product_type

                try:
                    category = Category.objects.get(slug=category)
                except Category.DoesNotExist:
                    print('Category ({}) for product ({}) does not exist, creating...'.format(category, name))
                    category = Category.objects.create(slug=category, name=category.title())

                product.category = category

                product.name = name
                product.description = description
                product.price = price
                product.is_published = is_published

                if variant_name:
                    product_var.name = variant_name

                if variant_price:
                    product_var.price_override = variant_price

                try:
                    product_attribute = ProductAttribute.objects.get(slug=attribute_slug)
                except ProductAttribute.DoesNotExist:
                    print('Product attribute ({}) for product ({}) does not exist, creating...'.format(attribute, name))
                    product_attribute = ProductAttribute.objects.create(slug=attribute_slug, name=attribute.title())

                try:
                    product_attribute_value = AttributeChoiceValue.objects.get(slug=attribute_value_slug)
                except AttributeChoiceValue.DoesNotExist:
                    product_attribute_value = AttributeChoiceValue()
                    product_attribute_value.attribute = product_attribute
                    product_attribute_value.slug = attribute_value_slug
                    product_attribute_value.name = attribute_value.title()
                    product_attribute_value.save()

                product_var_attrs = dict()
                product_var_attrs[product_attribute.pk] = product_attribute_value.pk
                product_var.attributes = product_var_attrs
                product_var.product = product

                try:
                    product.save()
                except Exception:
                    import pdb;pdb.set_trace()
                product_var.save()
                print('Product added successfully')
