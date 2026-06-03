import Lake
open Lake DSL

package «uav-formal» where
  -- Keep this package isolated from the Python simulator.

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.29.1"

lean_lib Uav where
