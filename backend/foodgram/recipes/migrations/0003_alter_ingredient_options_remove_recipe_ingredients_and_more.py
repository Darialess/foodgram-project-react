# Generated by Django 4.1.7 on 2023-02-18 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_ingredientrecipe_remove_recipe_ingridients_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'verbose_name': 'Ингредиент'},
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='ingredients',
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredient',
            field=models.ManyToManyField(through='recipes.IngredientRecipe', to='recipes.ingredient', verbose_name='Ингредиенты'),
        ),
    ]
