CREATE DATABASE IF NOT EXISTS vitracka
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE vitracka;

CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY ix_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS physical_profiles (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    gender VARCHAR(20) NOT NULL,
    weight FLOAT NOT NULL,
    height FLOAT NOT NULL,
    age INT NOT NULL,
    activity_level VARCHAR(30) NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    KEY ix_physical_profiles_user_id (user_id),
    CONSTRAINT fk_physical_profiles_user_id
        FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS goals (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    objective VARCHAR(30) NOT NULL,
    is_active BOOL NOT NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    KEY ix_goals_user_id (user_id),
    CONSTRAINT fk_goals_user_id
        FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS nutrition_plans (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    calories INT NOT NULL,
    protein INT NOT NULL,
    carbs INT NOT NULL,
    fat INT NOT NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    KEY ix_nutrition_plans_user_id (user_id),
    CONSTRAINT fk_nutrition_plans_user_id
        FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS meal_suggestions (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    nutrition_plan_id INT NOT NULL,
    meals_json TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    KEY ix_meal_suggestions_user_id (user_id),
    CONSTRAINT fk_meal_suggestions_user_id
        FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_meal_suggestions_nutrition_plan_id
        FOREIGN KEY (nutrition_plan_id) REFERENCES nutrition_plans (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS progress_check_ins (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    weight FLOAT NOT NULL,
    waist FLOAT NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    KEY ix_progress_check_ins_user_id (user_id),
    CONSTRAINT fk_progress_check_ins_user_id
        FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
