function formatTime(secondsTotal) {
  const days = Math.floor(secondsTotal / (3600 * 24));
  const hours = Math.floor((secondsTotal % (3600 * 24)) / 3600);
  const mins = Math.floor((secondsTotal % 3600) / 60);
  const secs = secondsTotal % 60;

  // Array mit allen Einheiten in Reihenfolge (höchste zu niedrigste)
  const units = [
    { value: days, label: "day" },
    { value: hours, label: "hour" },
    { value: mins, label: "minute" },
    { value: secs, label: "second" },
  ];

  // Index des höchsten Elements, das > 0 ist finden
  const firstNonZeroIndex = units.findIndex((unit) => unit.value > 0);

  // Falls alle 0 sind (z.B. 0 Sekunden), zeige "0 seconds"
  if (firstNonZeroIndex === -1) {
    return "0 seconds";
  }

  // Ab dem höchsten nicht-null Element alle Einheiten einschließen (auch wenn 0)
  const parts = units.slice(firstNonZeroIndex).map((unit) => {
    return `${unit.value} ${unit.label}${unit.value !== 1 ? "s" : ""}`;
  });

  if (parts.length === 1) return parts[0];
  if (parts.length === 2) return parts[0] + " and " + parts[1];
  return parts.slice(0, -1).join(", ") + ", and " + parts[parts.length - 1];
}

function formatTimeNoSeconds(secondsTotal) {
  const days = Math.floor(secondsTotal / (3600 * 24));
  const hours = Math.floor((secondsTotal % (3600 * 24)) / 3600);
  const mins = Math.floor((secondsTotal % 3600) / 60);

  const units = [
    { value: days, label: "day" },
    { value: hours, label: "hour" },
    { value: mins, label: "minute" },
  ];

  // Höchste nicht-null Einheit finden
  const firstNonZeroIndex = units.findIndex((unit) => unit.value > 0);

  if (firstNonZeroIndex === -1) {
    // Wenn alles 0 ist (also weniger als 1 Minute)
    return "less than a minute";
  }

  // Alle Einheiten ab dem höchsten nicht-null Element anzeigen (auch wenn 0)
  const parts = units.slice(firstNonZeroIndex).map((unit) => {
    return `${unit.value} ${unit.label}${unit.value !== 1 ? "s" : ""}`;
  });

  if (parts.length === 1) return parts[0];
  if (parts.length === 2) return parts[0] + " and " + parts[1];
  return parts.slice(0, -1).join(", ") + ", and " + parts[parts.length - 1];
}

function createTimeBlock(value, label) {
  return `<div class="time-block">
        <div class="time-value">${value}</div>
        <div class="time-label">${label}</div>
    </div>`;
}

function formatTimeBlocks(secondsTotal) {
  const days = Math.floor(secondsTotal / (3600 * 24));
  const hours = Math.floor((secondsTotal % (3600 * 24)) / 3600);
  const mins = Math.floor((secondsTotal % 3600) / 60);
  const secs = secondsTotal % 60;

  let blocks = [];
  if (days > 0) blocks.push(createTimeBlock(days, days === 1 ? "day" : "days"));
  if (hours > 0)
    blocks.push(createTimeBlock(hours, hours === 1 ? "hour" : "hours"));
  if (mins > 0)
    blocks.push(createTimeBlock(mins, mins === 1 ? "minute" : "minutes"));
  blocks.push(createTimeBlock(secs, secs === 1 ? "second" : "seconds"));

  return blocks.join("");
}
