<?php
  // Get all HTTP headers from the incoming request
  $headers = getallheaders();

  // Extract the CPEE callback URL from headers and save it to a local file
  // This URL will be used later by callback.php to forward data back to CPEE
  file_put_contents('callback.url', $headers['Cpee-Callback']);

  // Send response header to confirm callback registration with CPEE
  header('CPEE-CALLBACK: true');

  // Terminate script execution
  exit;
?>
