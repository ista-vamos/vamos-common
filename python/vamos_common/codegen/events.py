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
            wr(
                "#ifndef VAMOS_CODEGEN_EVENTS_EVENTS_H_\n#define VAMOS_CODEGEN_EVENTS_EVENTS_H_\n\n"
            )
            # wr("#ifdef DEBUG\n")
            wr("#include <iostream>\n")
            wr('#include "event_and_id.h"\n')
            # wr("#endif\n\n")
            wr("#include <vamos-buffers/cpp/event.h>\n\n")
            wr("using vamos::Event;\n\n")

            wr("enum class Kind : vms_kind {\n")
            wr("  END = Event::doneKind(),\n")
            for n, event in enumerate(events):
                wr(
                    f'  {event.name.name}{" = Event::firstValidKind()" if n == 0 else ""},\n'
                )
            wr("};\n\n")

            for event in events:
                sname = event.name.name
                ename = f"Event_{sname}"
                wr(f"struct {ename} : public Event {{\n")
                for field in event.fields:
                    wr(f"  {cpp_type(field.type())} {field.name.name}; // {field}\n")
                wr("\n")

                wr(f"  {ename}() = default;\n")
                wr(
                    f"  {ename}(vms_eventid id) : Event((vms_kind)Kind::{sname}, id) {{}}\n"
                )

                if event.fields:
                    params_str = ", ".join(
                        (
                            f"{cpp_type(field.type())} _{field.name.name}"
                            for field in event.fields
                        )
                    )
                    init_str = ", ".join(
                        (
                            f"{field.name.name}(_{field.name.name})"
                            for field in event.fields
                        )
                    )
                    wr(
                        f"  {ename}({params_str}) : Event((vms_kind)Kind::{sname}, 0), {init_str} {{}}\n"
                    )

                wr("\n")
                wr(f"  bool operator==(const {ename}& rhs) const {{\n")
                wr("    return ")
                if event.fields:
                    for n, field in enumerate(event.fields):
                        if n > 0:
                            wr(" && ")
                        wr(f"{field.name.name} == rhs.{field.name.name}")
                else:
                    wr("true")
                wr(";\n  }\n")
                wr(
                    f"  bool operator!=(const {ename} &rhs) const {{ return !operator==(rhs); }}\n\n"
                )
                wr(f"}};\n\n")

                # wr("#ifdef DEBUG\n")
                wr(f"std::ostream &operator<<(std::ostream &s, const {ename} &ev);\n")
                wr(
                    f"std::ostream &operator<<(std::ostream &s, const EventAndID<{ename}> &);\n\n"
                )
                # wr("#endif\n\n")

            wr("#endif\n")

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
        wr(
            f'  s << color_blue << "{sname}" << color_reset\n'
            f'    << "(" << color_red << std::setw(2) << std::right << {id_str} << color_reset;\n'
        )

        if not event.fields:
            wr(f'  s << ")";\n')
        else:
            wr(f'  s << ";; ";\n')
            for n, field in enumerate(event.fields):
                if n > 1:
                    wr(f'  s << ", ";\n')
                wr(f'  s << "{field.name.name}=" << ev.{field.name.name};\n')
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
                self._gen_print_event(wr, event, "ev.id()")
                wr("}\n\n")

                wr(
                    f"std::ostream &operator<<(std::ostream &s, const EventAndID<{ename}>& data) {{\n"
                )
                wr("  const auto& ev = data.event;\n")
                self._gen_print_event(wr, event, "data.id")
                wr("}\n\n")

            # wr("#endif\n")
