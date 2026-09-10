"""Generate Android components into an existing project."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from android_mcp.errors import ValidationError
from android_mcp.inspect import find_root, inspect_project
from android_mcp.scaffold import package_to_path

KINDS = (
    "activity",
    "fragment",
    "compose_screen",
    "viewmodel",
    "repository",
    "service",
    "broadcast_receiver",
    "content_provider",
    "room_entity",
    "retrofit_api",
    "notification",
)


def _pkg(report: dict[str, Any]) -> str:
    return report.get("namespace") or report.get("application_id") or "com.example.app"


def _src(root: Path, module: str, pkg: str) -> Path:
    return root / module / "src/main/java" / package_to_path(pkg)


def create_component(project: Path, kind: str, name: str, module: str | None = None) -> dict[str, Any]:
    kind = kind.lower().replace("-", "_")
    if kind not in KINDS:
        raise ValidationError(f"kind must be one of {KINDS}")
    if not name or not name[0].isalpha():
        raise ValidationError("name must be a class name")
    root = find_root(project)
    report = inspect_project(root)
    mod = module or report.get("application_module") or "app"
    pkg = _pkg(report)
    src = _src(root, mod, pkg)
    src.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    fn = globals()[f"_gen_{kind}"]
    written.extend(fn(src, pkg, name, root, mod, report))
    return {"kind": kind, "name": name, "module": mod, "package": pkg, "files": written}


def _put(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.lstrip("\n"), encoding="utf-8")
    return str(path)


def _gen_activity(src, pkg, name, root, mod, report):
    cls = name if name.endswith("Activity") else name + "Activity"
    p = src / f"{cls}.kt"
    if report.get("compose"):
        body = f'''
package {pkg}
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.Text
class {cls} : ComponentActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContent {{ Text("{cls}") }}
    }}
}}
'''
    else:
        body = f'''
package {pkg}
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
class {cls} : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
    }}
}}
'''
    return [_put(p, body)]


def _gen_fragment(src, pkg, name, root, mod, report):
    cls = name if name.endswith("Fragment") else name + "Fragment"
    return [_put(src / f"{cls}.kt", f'''
package {pkg}
import androidx.fragment.app.Fragment
class {cls} : Fragment()
''')]


def _gen_compose_screen(src, pkg, name, root, mod, report):
    cls = name if name.endswith("Screen") else name + "Screen"
    ui = src / "ui"
    return [_put(ui / f"{cls}.kt", f'''
package {pkg}.ui
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
@Composable
fun {cls}() {{ Text(text = "{cls}") }}
''')]


def _gen_viewmodel(src, pkg, name, root, mod, report):
    cls = name if name.endswith("ViewModel") else name + "ViewModel"
    return [_put(src / "ui" / f"{cls}.kt", f'''
package {pkg}.ui
import androidx.lifecycle.ViewModel
class {cls} : ViewModel()
''')]


def _gen_repository(src, pkg, name, root, mod, report):
    cls = name if name.endswith("Repository") else name + "Repository"
    return [_put(src / "data" / f"{cls}.kt", f'''
package {pkg}.data
class {cls}
''')]


def _gen_service(src, pkg, name, root, mod, report):
    cls = name if name.endswith("Service") else name + "Service"
    return [_put(src / f"{cls}.kt", f'''
package {pkg}
import android.app.Service
import android.content.Intent
import android.os.IBinder
class {cls} : Service() {{
    override fun onBind(intent: Intent?): IBinder? = null
}}
''')]


def _gen_broadcast_receiver(src, pkg, name, root, mod, report):
    cls = name if name.endswith("Receiver") else name + "Receiver"
    return [_put(src / f"{cls}.kt", f'''
package {pkg}
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
class {cls} : BroadcastReceiver() {{
    override fun onReceive(context: Context, intent: Intent) {{}}
}}
''')]


def _gen_content_provider(src, pkg, name, root, mod, report):
    cls = name if name.endswith("Provider") else name + "Provider"
    return [_put(src / f"{cls}.kt", f'''
package {pkg}
import android.content.ContentProvider
import android.content.ContentValues
import android.database.Cursor
import android.net.Uri
class {cls} : ContentProvider() {{
    override fun onCreate(): Boolean = true
    override fun query(uri: Uri, p: Array<out String>?, s: String?, a: Array<out String>?, o: String?): Cursor? = null
    override fun getType(uri: Uri): String? = null
    override fun insert(uri: Uri, values: ContentValues?): Uri? = null
    override fun delete(uri: Uri, s: String?, a: Array<out String>?): Int = 0
    override fun update(uri: Uri, values: ContentValues?, s: String?, a: Array<out String>?): Int = 0
}}
''')]


def _gen_room_entity(src, pkg, name, root, mod, report):
    entity = name if not name.endswith("Entity") else name
    return [
        _put(src / "data" / f"{entity}.kt", f'''
package {pkg}.data
import androidx.room.Entity
import androidx.room.PrimaryKey
@Entity(tableName = "{entity.lower()}")
data class {entity}(@PrimaryKey val id: Long, val name: String)
'''),
        _put(src / "data" / f"{entity}Dao.kt", f'''
package {pkg}.data
import androidx.room.Dao
import androidx.room.Query
@Dao
interface {entity}Dao {{
    @Query("SELECT * FROM {entity.lower()}")
    suspend fun all(): List<{entity}>
}}
'''),
    ]


def _gen_retrofit_api(src, pkg, name, root, mod, report):
    cls = name if name.endswith("Api") else name + "Api"
    return [_put(src / "data" / f"{cls}.kt", f'''
package {pkg}.data
import retrofit2.http.GET
interface {cls} {{
    @GET("ping")
    suspend fun ping(): String
}}
''')]


def _gen_notification(src, pkg, name, root, mod, report):
    cls = name if name.endswith("Notifier") else name + "Notifier"
    return [_put(src / f"{cls}.kt", f'''
package {pkg}
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import androidx.core.app.NotificationCompat
object {cls} {{
    fun ensureChannel(context: Context, id: String = "default") {{
        if (Build.VERSION.SDK_INT >= 26) {{
            val mgr = context.getSystemService(NotificationManager::class.java)
            mgr.createNotificationChannel(NotificationChannel(id, id, NotificationManager.IMPORTANCE_DEFAULT))
        }}
    }}
    fun build(context: Context, title: String, text: String) =
        NotificationCompat.Builder(context, "default").setContentTitle(title).setContentText(text).setSmallIcon(android.R.drawable.ic_dialog_info).build()
}}
''')]
