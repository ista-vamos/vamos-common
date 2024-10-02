from .codegen import CodeGen
from .lang.cpp import cpp_type

from vamos_common.types.type import StringType


class CodeGenCpp(CodeGen):
    def __init__(self, args, ctx, vamos_compatible=True):
        super().__init__(args, ctx)
        self._vamos_compatible = vamos_compatible

    def generate(self, events):
        self._gen_h(events)
        self._gen_cpp(events)

    def _gen_h(self, events):
        vamos_compatible = self._vamos_compatible

        with self.new_file("event.h") as f:
            wr = f.write
            wr(
                "#ifndef VAMOS_CODEGEN_EVENTS_EVENT_H_\n"
                "#define VAMOS_CODEGEN_EVENTS_EVENT_H_\n\n"
            )

            if vamos_compatible:
                wr("#include <vamos-buffers/cpp/event.h>\n\n")

                wr("enum class Kind : vms_kind {\n")
            else:
                wr("enum class Kind {\n")
            wr("  END,\n")
            for n, event in enumerate(events):
                wr(
                    f'  {event.name.name},\n'
                )
            wr("};\n\n")

            if vamos_compatible:
                wr("using Event = vamos::Event;\n\n")
            else:
                wr("""
                   class Event {
                     Kind _kind;

                   public:
                     Event(Kind k) : _kind(k) {};
                     Kind kind() const { return _kind; }

                   };\n

                   """)

            wr("#endif\n")

        with self.new_file("event_and_id.h") as f:

            f.write(f"""
                #ifndef VAMOS_EVENT_AND_ID_H
                #define VAMOS_EVENT_AND_ID_H\n\n

                #include "event.h"

                template <typename EventTy, typename IdTy = unsigned>
                struct EventAndID {{
                    const EventTy& event;
                    IdTy id;

                    explicit EventAndID(const EventTy& ev, IdTy id) : event(ev), id(id) {{}}
                }};

                #endif
            """)


        with self.new_file("events.h") as f:
            wr = f.write
            wr(
                "#ifndef VAMOS_CODEGEN_EVENTS_EVENTS_H_\n"
                "#define VAMOS_CODEGEN_EVENTS_EVENTS_H_\n\n"
            )
            # FIXME: include `cstdint` only when needed
            wr('#include <cstdint>\n')
            wr('#include "event.h"\n')

            # wr("#ifdef DEBUG\n")
            wr("#include <iostream>\n")
            wr('#include "event_and_id.h"\n')
            # wr("#endif\n\n")
            wr("\n")

            wr("struct TraceEvent : Event {\n")
            wr("  union {\n")
            for event in events:
                sname = event.name.name
                wr(f"    struct _{sname} {{\n")
                for field in event.fields:
                    wr(
                        f"      {cpp_type(field.type())} {field.name.name}; // {field}\n"
                    )
                wr(f"      bool operator==(const _{sname}& rhs) const {{\n")
                wr("        return ")
                if event.fields:
                    for n, field in enumerate(event.fields):
                        if n > 0:
                            wr(" && ")
                        wr(f"{field.name.name} == rhs.{field.name.name}")
                else:
                    wr("true")
                wr(";\n      }\n")
                wr(f"    }} {sname};\n")

            wr("  } data;\n\n")

            wr("  TraceEvent() = default;\n")
            wr("  TraceEvent(Kind k) : Event(k) {}\n")
            if vamos_compatible:
                wr("  TraceEvent(Kind k, vms_eventid id) : Event(k, id) {}\n")
                wr("  TraceEvent(vms_kind k, vms_eventid id) : Event(k, id) {}\n")

            wr(
                "  bool operator==(const TraceEvent &rhs) const {\n"
                "    if (kind() != rhs.kind()) return false;\n"
                "    switch (kind()) {\n"
                "      case Kind::END: return true;\n"
            )
            for event in events:
                sname = event.name.name
                wr(
                    f"      case Kind::{sname}: return data.{sname} == rhs.data.{sname};\n"
                )
            wr(f"      default: abort();\n")
            wr("    }\n  }\n\n")

            wr(
                "  bool operator!=(const TraceEvent &rhs) const { return !operator==(rhs); }\n"
            )
            wr("};\n\n")

            for event in events:
                self._gen_event(event, wr)

            wr("#endif\n")

    def _gen_event(self, event, wr):
        vamos_compatible = self._vamos_compatible

        sname = event.name.name
        ename = f"Event_{sname}"
        wr(f"struct {ename} : public TraceEvent {{\n")
        wr(f"  {ename}()  = default;\n")
        if vamos_compatible:
            wr(
                f"  {ename}(vms_eventid id) : Event((vms_kind)Kind::{sname}, id) {{}}\n"
            )

        if event.fields:
            params_str = ", ".join(
                (
                    f"{cpp_type(field.type())} {field.name.name}"
                    for field in event.fields
                )
            )
            init_str = "\n".join(
                (
                    f"data.{sname}.{field.name.name} = {field.name.name};"
                    for field in event.fields
                )
            )
            if vamos_compatible:
                wr(
                    f"  {ename}(vms_eventid id, {params_str}) : TraceEvent(Kind::{sname}, id), {init_str} {{}}\n"
                )
            else:
                wr(
                    f"  {ename}({params_str}) : TraceEvent(Kind::{sname}){{ {init_str} }}\n"
                )
        wr("\n")
        for field in event.fields:
            wr(f'  auto {field.name.name}() const {{ return data.{sname}.{field.name.name}; }}\n')
        wr(f"}};\n\n")
        wr(f'static_assert(sizeof({ename}) == sizeof(TraceEvent), "ABI mismatch! {ename} should be just a convenient wrapper around TraceEvent.");\n\n')
        # wr("#ifdef DEBUG\n")
        wr(f"std::ostream &operator<<(std::ostream &s, const {ename} &ev);\n")
        wr(
            f"std::ostream &operator<<(std::ostream &s, const EventAndID<{ename}> &);\n\n"
        )
        # wr("#endif\n\n")

    def _events_cpp_begin(self, wr):
        wr(
            "#include <cassert>\n\n"
            '#include "events.h"\n\n'
            # "#ifdef DEBUG\n"
            "#include <iomanip>\n"
            "#include <iostream>\n\n"
            'static const char *color_green = "\033[0;32m";\n'
            'static const char *color_red = "\033[0;31m";\n'
            'static const char *color_blue = "\033[1;34m";\n'
            'static const char *color_reset = "\033[0m";\n\n'
        )

    def _gen_print_event(self, wr, event, id_str):
        sname = event.name.name

        # print event name
        wr(
            f'  s << color_blue << "{sname}" << color_reset << "(";\n'
        )

        # print ID
        if self._vamos_compatible:
            wr(f'  s << color_red << std::setw(2) << std::right << {id_str} << color_reset;\n')

        # print fields
        if not event.fields:
            wr(f'  s << ")";\n')
        else:
            wr(f'  s << ", ";\n')
            for n, field in enumerate(event.fields):
                if n > 0:
                    wr(f'  s << ", ";\n')
                if isinstance(field.type(), StringType):
                    wr(
                        f'  s << "{field.name.name}=\\"" << ev.data.{sname}{field.name.name} << "\\"";\n'
                    )
                else:
                    wr(f'  s << "{field.name.name}=" << ev.data.{sname}.{field.name.name};\n')
            wr('  s << ")";\n\n')
        wr("  return s;\n")

    def _gen_cpp(self, events):
        with self.new_file("events.cpp") as f:
            wr = f.write

            self._events_cpp_begin(wr)

            for event in events:
                sname = event.name.name
                ename = f"Event_{sname}"
                wr(f"std::ostream &operator<<(std::ostream &s, const {ename} &ev) {{\n")
                self._gen_print_event(wr, event, "ev.get_id()")
                wr("}\n\n")

                wr(
                    f"std::ostream &operator<<(std::ostream &s, const EventAndID<{ename}>& data) {{\n"
                )
                wr("  const auto& ev = data.event;\n")
                self._gen_print_event(wr, event, "data.id")
                wr("}\n\n")

            # wr("#endif\n")
