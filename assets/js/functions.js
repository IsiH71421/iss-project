function formatTime(secondsTotal) {
  const days = Math.floor(secondsTotal / (3600 * 24));
  const hours = Math.floor((secondsTotal % (3600 * 24)) / 3600);
  const mins = Math.floor((secondsTotal % 3600) / 60);
  const secs = secondsTotal % 60;

  // Array with all time units in order (highest to lowest)
  const units = [
    { value: days, label: "day" },
    { value: hours, label: "hour" },
    { value: mins, label: "minute" },
    { value: secs, label: "second" },
  ];

  // Find index of highest non-zero element
  const firstNonZeroIndex = units.findIndex((unit) => unit.value > 0);

  // If all are 0 (e.g. 0 seconds), show "0 seconds"
  if (firstNonZeroIndex === -1) {
    return "0 seconds";
  }

  // Include all units from highest non-zero element (even if 0)
  const parts = units.slice(firstNonZeroIndex).map((unit) => {
    return `${unit.value} ${unit.label}${unit.value !== 1 ? "s" : ""}`;
  });

  if (parts.length === 1) return parts[0];
  if (parts.length === 2) return parts[0] + " and " + parts[1];
  return parts.slice(0, -1).join(", ") + ", and " + parts[parts.length - 1];
}

// Format time for forecast display where seconds should not be displayed
function formatTimeNoSeconds(secondsTotal) {
  const days = Math.floor(secondsTotal / (3600 * 24));
  const hours = Math.floor((secondsTotal % (3600 * 24)) / 3600);
  const mins = Math.floor((secondsTotal % 3600) / 60);

  const units = [
    { value: days, label: "day" },
    { value: hours, label: "hour" },
    { value: mins, label: "minute" },
  ];

  // Find highest non-zero unit
  const firstNonZeroIndex = units.findIndex((unit) => unit.value > 0);

  if (firstNonZeroIndex === -1) {
    // If everything is 0 (less than 1 minute)
    return "less than a minute";
  }

  // Include all units from highest non-zero element (even if 0)
  const parts = units.slice(firstNonZeroIndex).map((unit) => {
    return `${unit.value} ${unit.label}${unit.value !== 1 ? "s" : ""}`;
  });

  if (parts.length === 1) return parts[0];
  if (parts.length === 2) return parts[0] + " and " + parts[1];
  return parts.slice(0, -1).join(", ") + ", and " + parts[parts.length - 1];
}

// Create HTML time block element for countdown display
function createTimeBlock(value, label) {
  return `<div class="time-block">
        <div class="time-value">${value}</div>
        <div class="time-label">${label}</div>
    </div>`;
}

// Format seconds into HTML time blocks for countdown display
function formatTimeBlocks(secondsTotal) {
  const days = Math.floor(secondsTotal / (3600 * 24));
  const hours = Math.floor((secondsTotal % (3600 * 24)) / 3600);
  const mins = Math.floor((secondsTotal % 3600) / 60);
  const secs = secondsTotal % 60;

  // Array with all time units in order (highest to lowest)
  const units = [
    { value: days, label: "day" },
    { value: hours, label: "hour" },
    { value: mins, label: "minute" },
    { value: secs, label: "second" },
  ];

  // Find index of highest non-zero element
  const firstNonZeroIndex = units.findIndex((unit) => unit.value > 0);

  // If all are 0 (e.g. 0 seconds), show only seconds block
  if (firstNonZeroIndex === -1) {
    return createTimeBlock(0, "seconds");
  }

  // Include all units from highest non-zero element (even if 0)
  const blocks = units.slice(firstNonZeroIndex).map((unit) => {
    return createTimeBlock(
      unit.value,
      unit.value === 1 ? unit.label : unit.label + "s"
    );
  });

  return blocks.join("");
}
