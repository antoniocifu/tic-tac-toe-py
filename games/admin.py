from django.contrib import admin

from games.models import Game, Move


class MoveInline(admin.TabularInline):
    model = Move
    extra = 0
    readonly_fields = ("number", "mark", "row", "col", "played_by", "played_at")
    can_delete = False


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id", "player_x", "player_o", "status", "winner", "created_at")
    list_filter = ("status",)
    search_fields = ("player_x__username", "player_o__username")
    readonly_fields = ("created_at", "updated_at")
    inlines = [MoveInline]


@admin.register(Move)
class MoveAdmin(admin.ModelAdmin):
    list_display = ("id", "game", "number", "mark", "row", "col", "played_by", "played_at")
    list_filter = ("mark",)
    search_fields = ("game__id",)
