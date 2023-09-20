from .codegen import CodeGen


class CodeGenCpp(CodeGen):

    def generate(self, tracetypes, htracetypes, alphabet):
        self._gen_h(tracetypes, htracetypes)
        self._gen_cpp(tracetypes, htracetypes)

    def _gen_h(self, tracetypes, htracetypes):
        # name_to_ev = {ev.name.name: ev for ev in eventdecls}

        with self.new_file("traces.h") as f:
            wr = f.write
            wr("#ifndef VAMOS_CODEGEN_TRACES_H_\n#define VAMOS_CODEGEN_TRACES_H_\n\n")
            wr("#include <iostream>\n\n")
            wr('#include "trace.h"\n')
            wr('#include "htrace.h"\n')
            wr('#include "event_and_id.h"\n')
            wr('#include "stdout_trace.h"\n')
            wr("#include <vamos-buffers/cpp/event.h>\n\n")
            wr("using vamos::Event;\n\n")

            for ty, tracety in tracetypes.items():
                self._gen_trace_ty(wr, ty, tracety)


            for ty, htracety in htracetypes.items():
                self._gen_hypertrace_ty(wr, ty, htracety)

            wr("#endif")

    def _gen_trace_ty(self, wr, ty, tracety):
        name = tracety.name
        ###
        ## Event in the trace `name`
        ename = f"Event_{name}"
        wr(f"union {ename} {{\n")
        wr("  Event base;\n")
        for event_ty in ty.subtypes:
            sname = event_ty.name
            wr(f"  Event_{sname} {sname};\n")
        wr("\n")

        wr(f"  {ename}() : base() {{}}\n")
        for event_ty in ty.subtypes:
            sname = event_ty.name
            wr(f"  {ename}(const Event_{sname}& ev) : {sname}(ev) {{}}\n")

        wr(f"  ~{ename}() {{\n" "     switch(base.get_kind()) {\n")
        for event_ty in ty.subtypes:
            sname = event_ty.name
            wr(
                f"     case (vms_kind)Kind::{sname}: {sname}.~Event_{sname}(); break;\n"
            )
        wr(f"     default: abort();\n")
        wr("      }\n")
        wr("  }\n")

        wr(
            "\n  template <Kind k> bool isa() const { return base.get_kind() == (vms_kind)k; }\n"
        )
        wr(f"  void set_id(vms_eventid id) {{ base.set_id(id); }}\n")
        wr(f"  vms_eventid id() const {{ return base.get_id(); }}\n")
        wr(f"  vms_kind kind() const {{ return base.get_kind(); }}\n")

        wr("};\n\n")

        wr(f"std::ostream &operator<<(std::ostream &s, const {ename} &ev);\n")
        wr("/* print the event with an explicitly given ID */\n")
        wr(
            f"std::ostream &operator<<(std::ostream &s, const EventAndID<{ename}> &);\n\n"
        )

        ###
        ## The trace itself
        if tracety.is_stdout():
            superclass = f"StdoutTrace<{ename}>"
        else:
            superclass = f"Trace<{ename}>"

        wr(f"class {name} : public {superclass} {{\n")
        wr("public:\n")
        tid = int(name[name.find("_") + 1:])
        wr(f"  constexpr static size_t TYPE_ID = {tid};\n\n")
        wr(f"  {name}(size_t id) : {superclass}(id, {tid}) {{}}\n")
        wr("};\n\n")

    def _gen_hypertrace_ty(self, wr, ty, tracety):
        name = tracety.name
        superclass = f"HTrace"

        wr(f"class {name} : public {superclass} {{\n")
        wr("public:\n")
        tid = int(name[name.find("_") + 1:])
        wr(f"  constexpr static size_t TYPE_ID = {tid};\n\n")
        wr(f"  {name}(size_t id) : {superclass}(id, {tid}) {{}}\n")
        wr("};\n\n")

    def _cpp_begin(self, wr):
        wr(
            "#include <cassert>\n\n"
            '#include "events.h"\n\n'
            '#include "traces.h"\n\n'
            "#include <iostream>\n\n"
            'static const char *color_green = "\033[0;32m";\n'
            'static const char *color_red = "\033[0;31m";\n'
            'static const char *color_reset = "\033[0m";\n\n'
        )

    def _gen_cpp(self, tracetypes, htracetypes):
        with self.new_file("traces.cpp") as f:
            wr = f.write

            self._cpp_begin(wr)

            for ty, tracety in tracetypes.items():
                name = tracety.name
                ###
                ## Event in the trace `name`
                ename = f"Event_{name}"

                wr(
                    f"std::ostream &operator<<(std::ostream &s, const {ename} &ev) {{\n"
                    f'  s << "{name}::";\n'
                )

                wr("  switch((Kind)ev.kind()) {\n")

                for event_ty in ty.subtypes:
                    sname = event_ty.name
                    wr(f"    case Kind::{sname}:\n" f"     s << ev.{sname}; break;\n")
                wr('    default: assert(false && "Invalid kind"); abort(); \n')
                wr("  }\n")

                wr("  return s;\n")
                wr("}\n\n")

                ### operator<< with EventAndID
                wr(
                    f"std::ostream &operator<<(std::ostream &s, const EventAndID<{ename}>& data) {{\n"
                    f'  s << "{name}::";\n'
                )

                wr("  switch((Kind)data.event.kind()) {\n")

                for event_ty in ty.subtypes:
                    sname = event_ty.name
                    wr(
                        f"    case Kind::{sname}:\n"
                        f"     s << EventAndID<Event_{sname}>(data.event.{sname}, data.id); break;\n"
                    )
                wr('    default: assert(false && "Invalid kind"); abort(); \n')
                wr("  }\n")

                wr("  return s;\n")
                wr("}\n\n")
