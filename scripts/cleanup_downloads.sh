#!/bin/bash
set -e

# Базовая директория проекта
BASE_DIR="/home/aspex/frame_draw_server"
DOWNLOAD_DIR="$BASE_DIR/static/downloads"

# --- Параметры политики хранения ---
RETENTION_DAYS=90      # сколько дней хранить (по дате каталога/mtime)
MAX_SIZE_GB=10         # максимальный общий объём static/downloads

# --- Проверка, что каталог существует ---
if [ ! -d "$DOWNLOAD_DIR" ]; then
  echo "[$(date)] DOWNLOAD_DIR not found: $DOWNLOAD_DIR" >&2
  exit 0
fi

echo "[$(date)] Cleanup started for $DOWNLOAD_DIR"

# --- 1) Удаляем каталоги старше RETENTION_DAYS ---
echo "[$(date)] Removing directories older than ${RETENTION_DAYS} days..."
find "$DOWNLOAD_DIR" -mindepth 1 -maxdepth 1 -type d -mtime +$RETENTION_DAYS -print -exec rm -rf {} \;

# --- 2) Контролируем максимальный размер ---
MAX_SIZE_KB=$((MAX_SIZE_GB * 1024 * 1024))  # из ГБ в КБ
CURRENT_SIZE_KB=$(du -s "$DOWNLOAD_DIR" | awk '{print $1}')

echo "[$(date)] Current size: ${CURRENT_SIZE_KB} KB, limit: ${MAX_SIZE_KB} KB"

if (( CURRENT_SIZE_KB > MAX_SIZE_KB )); then
  echo "[$(date)] Size is above limit – removing oldest directories..."

  # Список подкаталогов по времени изменения (самые старые первыми)
  mapfile -t DIRS < <(
    find "$DOWNLOAD_DIR" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' \
    | sort -n \
    | awk '{print $2}'
  )

  for dir in "${DIRS[@]}"; do
    # Пересчитываем размер
    CURRENT_SIZE_KB=$(du -s "$DOWNLOAD_DIR" | awk '{print $1}')
    if (( CURRENT_SIZE_KB <= MAX_SIZE_KB )); then
      break
    fi

    echo "[$(date)] Removing directory: $dir"
    rm -rf "$dir"
  done

  CURRENT_SIZE_KB=$(du -s "$DOWNLOAD_DIR" | awk '{print $1}')
  echo "[$(date)] Size after cleanup: ${CURRENT_SIZE_KB} KB"
else
  echo "[$(date)] Size is under limit, nothing to do."
fi

echo "[$(date)] Cleanup finished."
