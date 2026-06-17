#!/usr/bin/env python3
"""Pydantic models for Pac-Man configuration and save data.

All models use extra='ignore' so unknown config keys are silently
dropped (as required by the project spec: unknown keys must be ignored).
"""

from pydantic import BaseModel, ConfigDict, Field


class LevelsConfig(BaseModel):
    """Configuration for a single game level.

    Default values reproduce the first level, so a bare
    LevelsConfig(level=0) is a playable fallback level when no
    config file can be read.

    Attributes:
        level: Level index (0-20).
        width: Maze width in cells (10-50).
        height: Maze height in cells (10-50).
        lives: Starting lives for this level (0-10).
        pacgum: Number of pacgums placed in corridors (0-2000).
        points_per_pacgum: Score awarded per pacgum eaten (0-500).
        points_per_super_pacgum: Score per super-pacgum (0-500).
        points_per_ghost: Score per edible ghost eaten (0-500).
        seed: RNG seed used for maze generation.
        level_max_time: Time limit in seconds (0-320).
        ghosts_per_level: Number of ghosts spawned (0-10).
        ghost_speed: Ghost movement speed (0.0-1.0).
        pacman_speed: Pacman movement speed (0.0-1.0).
        scatter_timer: Scatter phase duration in seconds (0-300).
        frightened_timer: Edible phase duration in seconds (0-300).
        chase_timer: Chase phase duration in seconds (0-300).
    """

    model_config = ConfigDict(extra="ignore", frozen=True)

    level: int = Field(default=0, ge=0, le=20)
    width: int = Field(default=15, ge=7, le=50)
    height: int = Field(default=17, ge=7, le=50)
    lives: int = Field(default=3, ge=0, le=10)
    pacgum: int = Field(default=204, ge=0, le=2000)
    points_per_pacgum: int = Field(default=10, ge=0, le=500)
    points_per_super_pacgum: int = Field(default=50, ge=0, le=500)
    points_per_ghost: int = Field(default=200, ge=0, le=500)
    seed: int = Field(default=42)
    level_max_time: int = Field(default=90, ge=0, le=320)
    ghost_speed: float = Field(default=0.03, ge=0.0, le=1.0)
    pacman_speed: float = Field(default=0.06, ge=0.0, le=1.0)
    scatter_timer: float = Field(default=7.0, ge=0.0, le=300.0)
    frightened_timer: float = Field(default=15.0, ge=0.0, le=300.0)
    chase_timer: float = Field(default=20.0, ge=0.0, le=300.0)


class Metadata(BaseModel):
    """Global game metadata stored in the save file.

    Attributes:
        global_all_time_high_score: Best score ever recorded.
        last_updated: ISO date string of the last save.
    """

    model_config = ConfigDict(extra="ignore")

    global_all_time_high_score: int
    last_updated: str


class Player(BaseModel):
    """Per-player persistent data.

    Attributes:
        high_score: Player's personal best score (>= 0).
        classic_high_score: Best score in classic mode (>= 0).
        school_high_score: Best score in school mode (>= 0).
        school_current_level: Saved school-mode level (>= 0).
        classic_current_level: Saved classic-mode level (>= 0).
        date_created: ISO date string of account creation.
        last_played: ISO date string of the most recent save.
    """

    model_config = ConfigDict(extra="ignore")

    high_score: int = Field(ge=0)
    classic_high_score: int = Field(default=0, ge=0)
    school_high_score: int = Field(default=0, ge=0)
    school_current_level: int = Field(default=0, ge=0)
    classic_current_level: int = Field(default=0, ge=0)
    date_created: str
    last_played: str


class DataConfig(BaseModel):
    """Root save data model.

    Attributes:
        game_metadata: Global highscore and date metadata.
        players: Mapping of player name to their save data.
    """

    model_config = ConfigDict(extra="ignore")

    game_metadata: Metadata
    players: dict[str, Player]


class Settings:
    """Holds all toggleable game settings.

    Attributes:
        maze_42: True for 42 maze, False for original.
        cheat_mode: Whether cheat hotkeys are enabled in-game.
        sound: Whether sound is playing.
    """

    def __init__(self) -> None:
        """Initialize all settings to their default values."""
        self.maze_42: bool = True
        self.cheat_mode: bool = False
        self.sound: bool = True
        self.solo: bool = True


class GameState:
    """Snapshot of the game produced by Game.tick() each frame.

    Play reads this every frame to render the game.
    Game writes it every tick to reflect the current simulation state.

    Attributes:
        maze: 2D grid of the current level. Each cell is an int:
            0 = wall, 1 = corridor.
        pacman_pos: Pacman's current position as (x, y) floats,
            in maze-cell coordinates (e.g. 3.5 means between cells).
        ghosts: List of ghost positions as (x, y) floats, in the same
            coordinate space as pacman_pos. Index order is always
            [blinky, pinky, inky, clyde].
        ghosts_mode: Ghost AI mode per ghost, same indexing as ghosts.
            1 = chase (normal, colored), 2 = scatter (run to corner),
            3 = frightened (blue, edible).
        gums: 2D grid mirroring maze dimensions. Each cell is an int:
            0 = empty, 1 = pacgum, 2 = super-pacgum.
        paused: True while the game is paused. Game.tick() is a no-op
            when this is True; Play uses it to overlay the pause popup.
        over: True when the player has lost all lives. Play reads this
            to trigger the post-game save flow with status "lose".
        won: True when all levels are completed. Play reads this to
            trigger the post-game save flow with status "win".
        lives: Remaining lives. Displayed in the HUD.
        lost_life: True for exactly one frame after Pacman dies and
            respawns. Play uses this to trigger a death animation.
            Game resets it to False on the next tick.
        score: Cumulative score for the current session.
        level: Current level index (0-based). Displayed in the HUD.
        timer: Remaining time in seconds for the current level.
            Displayed in the HUD. Game decrements it each tick.
    """

    def __init__(self) -> None:
        """Initialize all fields to safe defaults."""
        self.maze: list[list[int]] = []
        self.width: int = 0
        self.height: int = 0
        self.pacman_pos: tuple[float, float] = (0.0, 0.0)
        self.pacman_direction: tuple[int, int] = (0, 0)
        self.ghosts: list[tuple[float, float]] = []
        self.ghosts_direction: list[tuple[int, int]] = []
        self.ghosts_mode: list[int] = []
        self.frightened_remaining: float = 0.0
        self.gums: list[list[int]] = []
        self.paused: bool = False
        self.over: bool = False
        self.won: bool = False
        self.lives: int = 3
        self.lost_life: bool = False
        self.timed_out: bool = False
        self.level_cleared: bool = False
        self.score: int = 0
        self.level: int = 0
        self.timer: float = 90.0
        self.fruits_eaten: int = 0
        self.eaten_fruit_types: list[int] = []
        self.cheat_invincible: bool = False
        self.cheat_speed: bool = False
        self.cheat_freeze: bool = False
