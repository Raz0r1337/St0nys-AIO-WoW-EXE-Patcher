$tokens = $null; $errors = $null
[void][System.Management.Automation.Language.Parser]::ParseFile($args[0], [ref]$tokens, [ref]$errors)
"parse errors: $($errors.Count)"; foreach ($e in $errors) { $e.Message }
