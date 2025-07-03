function formatTime(secondsTotal) {
  const days = Math.floor(secondsTotal / (3600 * 24));
  const hours = Math.floor((secondsTotal % (3600 * 24)) / 3600);
  const mins = Math.floor((secondsTotal % 3600) / 60);
  const secs = secondsTotal % 60;

  let parts = [];
  if (days > 0) parts.push(`${days} day${days !== 1 ? "s" : ""}`);
  if (hours > 0) parts.push(`${hours} hour${hours !== 1 ? "s" : ""}`);
  if (mins > 0) parts.push(`${mins} minute${mins !== 1 ? "s" : ""}`);
  parts.push(`${secs} second${secs !== 1 ? "s" : ""}`);

  if (parts.length === 1) return parts[0];
  if (parts.length === 2) return parts[0] + " and " + parts[1];
  return parts.slice(0, -1).join(", ") + ", and " + parts[parts.length - 1];
}

function formatTimeNoSeconds(secondsTotal) {
  const days = Math.floor(secondsTotal / (3600 * 24));
  const hours = Math.floor((secondsTotal % (3600 * 24)) / 3600);
  const mins = Math.floor((secondsTotal % 3600) / 60);

  let parts = [];
  if (days > 0) parts.push(`${days} day${days !== 1 ? "s" : ""}`);
  if (hours > 0) parts.push(`${hours} hour${hours !== 1 ? "s" : ""}`);
  if (mins > 0) parts.push(`${mins} minute${mins !== 1 ? "s" : ""}`);

  if (parts.length === 0) return "less than a minute";

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
