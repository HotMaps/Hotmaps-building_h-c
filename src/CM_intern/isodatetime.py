from datetime import datetime
from datetime import timezone

local_time = datetime.now(timezone.utc).astimezone()
dt = local_time.isoformat()
print(dt)