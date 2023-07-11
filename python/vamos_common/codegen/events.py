from .codegen import CodeGen
from .lang.cpp import cpp_type


class CodeGenCpp(CodeGen):
    def __init__(self, args, ctx):
        super().__init__(args, ctx)

    def generate(self, events):
        self._gen_h(events)
        self._gen_cpp(events)

    def _gen_h(self, events):
        with self.new_file("events.h") as f:
            wr = f.write
            wr("#ifndef OD_EVENTS_H_\n#define OD_EVENTS_H_\n\n")
            wr("#include <vamos-buffers/cpp/event.h>\n\n")
            wr("using vamos::Event;\n\n")

            wr("enum class Kind : vms_kind {\n")
            wr("  END = Event::doneKind(),\n")
            for n, event in enumerate(events):
                wr(
                    f'  {event.name.name}{" = Event::firstValidKind()" if n == 0 else ""},\n'
                )
            wr("};\n\n")

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
            wr("  TraceEvent(Kind k) : Event((vms_kind)k) {}\n")
            wr("  TraceEvent(Kind k, vms_eventid id) : Event((vms_kind)k, id) {}\n")
            wr("  TraceEvent(vms_kind k, vms_eventid id) : Event(k, id) {}\n")

            wr(
                "  bool operator==(const TraceEvent &rhs) const {\n"
                "    if (kind() != rhs.kind()) return false;\n"
                "    switch (kind()) {\n"
                "      case (vms_kind)Kind::END: return true;\n"
            )
            for event in events:
                sname = event.name.name
                wr(
                    f"      case (vms_kind)Kind::{sname}: return data.{sname} == rhs.data.{sname};\n"
                )
            wr(f"      default: abort();\n")
            wr("    }\n  }\n\n")

            wr(
                "  bool operator!=(const TraceEvent &rhs) const { return !operator==(rhs); }\n"
            )
            wr("};\n\n")

            for event in events:
                sname = event.name.name
                wr(f"// Wrapper around event `{sname}` for simple construction\n")
                wr(f"struct Event_{sname} : public TraceEvent {{\n")
                wr(f"  Event_{sname}() = default;\n")
                params = ", ".join(
                    (
                        f"{cpp_type(field._type)} {field.name.name}"
                        for field in event.fields
                    )
                )
                if params:
                    wr(f"  Event_{sname}({params}) : TraceEvent(Kind::{sname}) {{\n")
                    for field in event.fields:
                        wr(f"    data.{sname}.{field.name.name} = {field.name.name};\n")
                    wr("  }\n")
                    wr(
                        f"  Event_{sname}(vms_eventid id, {params}) : TraceEvent(Kind::{sname}, id) {{\n"
                    )
                    for field in event.fields:
                        wr(f"    data.{sname}.{field.name.name} = {field.name.name};\n")
                    wr("  }\n")
                else:
                    wr(f"  Event_{sname}() : TraceEvent(Kind::{sname}) {{}}\n")
                    wr(
                        f"  Event_{sname}(vms_eventid id) : TraceEvent(Kind::{sname}, id) {{}}\n"
                    )
                wr("};\n\n")
                wr(
                    f'static_assert(sizeof(TraceEvent) == sizeof(Event_{sname}), "TraceEvent and Event_{sname} have different size");\n\n'
                )

            if self.args.debug:
                wr(
                    "#include <iostream>\n"
                    "std::ostream &operator<<(std::ostream &s, const TraceEvent &ev);\n\n"
                )

            wr("#endif")

    def _events_cpp_begin(self, wr):
        wr(
            "#include <cassert>\n\n"
            '#include "events.h"\n\n'
            "#ifdef DBG\n"
            "#include <iomanip>\n"
            "#include <iostream>\n\n"
            'static const char *color_green = "\033[0;32m";\n'
            'static const char *color_red = "\033[0;31m";\n'
            'static const char *color_reset = "\033[0m";\n\n'
        )

    def _gen_cpp(self, events):
        with self.new_file("events.cpp") as f:
            wr = f.write

            self._events_cpp_begin(wr)

            wr(
                "std::ostream &operator<<(std::ostream &s, const TraceEvent &ev) {\n"
                '  s << "TraceEvent(" << color_green << std::setw(7) << std::left;\n'
            )

            wr("  switch((Kind)ev.kind()) {\n")
            wr(
                '    case Kind::END: s << "END" << color_reset'
                '                      << ", " << color_red << std::setw(2) << std::right << ev.id() << color_reset;\n'
                "      break;\n"
            )
            for event in events:
                wr(
                    f"    case Kind::{event.name.name}:\n"
                    f'      s << "{event.name.name}"\n'
                    '         << color_reset << ", " << color_red << std::setw(2)'
                    " << std::right << ev.id() << color_reset;\n"
                )

                if not event.fields:
                    continue
                for n, field in enumerate(event.fields):
                    wr(f'      s << ", ";\n')
                    wr(
                        f'      s << "{field.name.name}=" << ev.data.{event.name.name}.{field.name.name};\n'
                    )
                wr(f"      break;\n")

            wr('    default: s << "??"; assert(false && "Invalid kind"); break;\n')
            wr("  }\n")

            wr('  s << ")";\n\n')

            wr("  return s;\n")
            wr("}\n\n")
            wr("#endif\n")
