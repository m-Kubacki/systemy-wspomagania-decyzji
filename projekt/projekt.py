import graphviz
from opyenxes.data_in.XUniversalParser import XUniversalParser
from collections import defaultdict
from functools import reduce

# --- Konfiguracja ---
LOG_FILE_PATH = 'repairexample.xes' # Ścieżka do pliku XES
OUTPUT_HEURISTIC_BASE = 'heuristic_net'
OUTPUT_BPMN_BASE = 'alpha_bpmn_graph'

# Progi filtrowania dla Heuristic Miner
ACTIVITY_FREQUENCY_THRESHOLD = 0  # Minimalna liczba wystąpień aktywności, aby ją pokazać (0 = pokaż wszystkie)
TRANSITION_FREQUENCY_THRESHOLD = 0 # Minimalna liczba wystąpień przejścia, aby je pokazać (0 = pokaż wszystkie)

# Wybór trybu: 'heuristic' lub 'alpha'
MINER_TYPE = 'heuristic'
# MINER_TYPE = 'alpha'

# --- 1. Wczytywanie i Parsowanie Logu XES ---
try:
    with open(LOG_FILE_PATH) as log_file:
        log = XUniversalParser().parse(log_file)[0]
except FileNotFoundError:
    print(f"Błąd: Plik logu '{LOG_FILE_PATH}' nie został znaleziony.")
    exit()
except Exception as e:
    print(f"Błąd podczas parsowania pliku XES: {e}")
    exit()

print(f"Log '{LOG_FILE_PATH}' wczytany pomyślnie.")

# --- 2. Ekstrakcja Śladów Przepływu Pracy (Nazwy Aktywności) ---
workflow_log = []
for trace in log:
    workflow_trace = []
    for event in trace:
        try:
        
            attributes = event.get_attributes()
            if 'Activity' in attributes:
                 event_name = attributes['Activity'].get_value()
                 workflow_trace.append(event_name)
            elif 'concept:name' in attributes:
                 event_name = attributes['concept:name'].get_value()
                 workflow_trace.append(event_name)

        except Exception as e:
            print(f"Ostrzeżenie: Problem z odczytem atrybutu zdarzenia w śladzie {log.index(trace)}: {e}")

    if workflow_trace: # Dodajemy tylko niepuste ślady
        workflow_log.append(workflow_trace)

if not workflow_log:
    print("Błąd: Nie udało się wyekstrahować żadnych śladów przepływu pracy z logu. Sprawdź strukturę pliku XES i nazwy atrybutów.")
    exit()

print(f"Wyekstrahowano {len(workflow_log)} śladów.")

# --- 3. Obliczanie Częstotliwości Aktywności i Przejść ---
activity_counter = defaultdict(int)
transition_counter = defaultdict(int)
direct_succession_rel = defaultdict(set) # Dla relacji > (bezpośredniego następstwa)

for w_trace in workflow_log:
    if not w_trace: continue # Pomiń puste ślady

    # Zliczanie aktywności
    for activity in w_trace:
        activity_counter[activity] += 1

    # Zliczanie przejść i budowanie relacji bezpośredniego następstwa
    for i in range(len(w_trace) - 1):
        source_activity = w_trace[i]
        target_activity = w_trace[i+1]
        transition = (source_activity, target_activity)
        transition_counter[transition] += 1
        direct_succession_rel[source_activity].add(target_activity)

all_activities = set(activity_counter.keys())
if not all_activities:
    print("Błąd: Nie znaleziono żadnych aktywności w logu.")
    exit()

print(f"Znaleziono {len(all_activities)} unikalnych aktywności.")
# --- Implementacja Heuristic Miner ---

def generate_heuristic_graph(activity_counts, transition_counts, direct_succession, act_threshold, trans_threshold, filename_base):
    """Generuje graf heurystyczny z filtrowaniem i wizualizacją częstotliwości."""

    # Filtrowanie aktywności
    filtered_activities = {act for act, count in activity_counts.items() if count >= act_threshold}
    if not filtered_activities:
        print(f"Ostrzeżenie: Żadne aktywności nie spełniają progu częstotliwości {act_threshold}. Graf będzie pusty.")
        return None

    # Filtrowanie przejść
    filtered_transitions = {trans: count for trans, count in transition_counts.items()
                            if count >= trans_threshold and
                            trans[0] in filtered_activities and
                            trans[1] in filtered_activities}

    if not filtered_transitions and len(filtered_activities) > 1 : # Jeśli są aktywności, ale nie ma przejść
         print(f"Ostrzeżenie: Żadne przejścia nie spełniają progu częstotliwości {trans_threshold} (lub łączą odfiltrowane aktywności).")
         # Graf będzie zawierał tylko węzły


    G = graphviz.Digraph(comment='Heuristic Net')
    G.graph_attr['rankdir'] = 'LR' # Układ od lewej do prawej
    G.node_attr['shape'] = 'box'   # Domyślny kształt węzła (box dla aktywności)
    G.node_attr['style'] = 'rounded,filled'
    G.node_attr['fillcolor'] = '#FFFFCC' # Jasnożółty dla aktywności

    # Obliczanie min/max dla kolorów i grubości linii
    if activity_counts:
        min_act_freq = min(activity_counts.values()) if activity_counts else 1
        max_act_freq = max(activity_counts.values()) if activity_counts else 1
    else:
         min_act_freq, max_act_freq = 1, 1

    if filtered_transitions:
        min_trans_freq = min(filtered_transitions.values()) if filtered_transitions else 1
        max_trans_freq = max(filtered_transitions.values()) if filtered_transitions else 1
    else:
        min_trans_freq, max_trans_freq = 1, 1

    # Dodawanie węzłów (przefiltrowanych aktywności)
    for activity in filtered_activities:
        count = activity_counts[activity]
        label = f"{activity}\n({count})" # Etykieta z nazwą i częstotliwością

        # Skalowanie koloru na podstawie częstotliwości (od jasnego do ciemniejszego pomarańczowego)
        # Normalizacja do zakresu [0, 99] dla wartości szesnastkowej koloru
        color_intensity = 0
        if max_act_freq > min_act_freq:
             # Normalizujemy do 0-1, a potem mnożymy przez 99
             # Odwracamy, aby większa częstotliwość = ciemniejszy kolor (mniejsza wartość hex)
             normalized_freq = (count - min_act_freq) / (max_act_freq - min_act_freq)
             color_intensity = 99 - int(normalized_freq * 99) # Wartość od 0 (ciemny) do 99 (jasny)
        else: # Jeśli wszystkie mają tę samą częstotliwość
             color_intensity = 50 # Średni kolor

        # Formatowanie wartości szesnastkowej (00-FF), tutaj używamy 00-63 (99 dziesiętnie)
        hex_intensity = hex(color_intensity)[2:].zfill(2) # Zawsze dwie cyfry hex
        node_color = f"#FF9933{hex_intensity}" # Pomarańczowy z przezroczystością/intensywnością

        G.node(activity, label=label, fillcolor=node_color)

    # Dodawanie krawędzi (przefiltrowanych przejść)
    for (source, target), count in filtered_transitions.items():
        # Skalowanie grubości linii (np. od 1 do 6)
        penwidth = 1.0
        if max_trans_freq > min_trans_freq:
            # Liniowe skalowanie:
             normalized_penwidth = (count - min_trans_freq) / (max_trans_freq - min_trans_freq)
             penwidth = 1 + normalized_penwidth * 5 # Skala 1 do 6
        elif count > 0: # Jeśli wszystkie przejścia mają tę samą częstotliwość > 0
            penwidth = 2.0 # Ustawiamy średnią grubość

        G.edge(source, target, label=str(count), penwidth=str(penwidth))

    # Identyfikacja i dodawanie zdarzeń startowych i końcowych (heurystycznie)
    # Aktywności, które są źródłami w przefiltrowanych przejściach
    source_nodes_in_filtered_transitions = {trans[0] for trans in filtered_transitions}
    # Aktywności, które są celami w przefiltrowanych przejściach
    target_nodes_in_filtered_transitions = {trans[1] for trans in filtered_transitions}

    # Startowe: są w przefiltrowanych aktywnościach, ale nie są celem żadnego przefiltrowanego przejścia
    start_activities = filtered_activities - target_nodes_in_filtered_transitions
    # Końcowe: są w przefiltrowanych aktywnościach, ale nie są źródłem żadnego przefiltrowanego przejścia
    end_activities = filtered_activities - source_nodes_in_filtered_transitions

    # Dodaj węzły Start/End tylko jeśli istnieją odpowiednie aktywności
    if start_activities:
        G.node("start", shape="circle", label="", fillcolor="#90EE90", width="0.3", fixedsize="true") # Zielony
        for activity in start_activities:
            G.edge("start", activity)

    if end_activities:
        G.node("end", shape="doublecircle", label="", fillcolor="#FFB6C1", width="0.3", fixedsize="true") # Różowy/Czerwony
        for activity in end_activities:
           
            try:
                 G.node(activity) # Sprawdza czy węzeł istnieje, jeśli nie - Graphviz go doda
                 G.edge(activity, "end")
            except KeyError: # Chociaż Graphviz sam doda węzeł, lepiej być pewnym
                 print(f"Ostrzeżenie: Aktywność końcowa {activity} nie była w filtered_activities, ale została zidentyfikowana jako końcowa. Pomijanie krawędzi do 'end'.")


    # Zapis i renderowanie
    try:
        output_filename_dot = f"{filename_base}_filtered_act{act_threshold}_trans{trans_threshold}.gv"
        output_filename_png = f"{filename_base}_filtered_act{act_threshold}_trans{trans_threshold}.png"
        G.render(output_filename_dot, view=False, format='png', outfile=output_filename_png) # Zapisuje .gv i .png
        print(f"Graf heurystyczny zapisany jako '{output_filename_png}' i '{output_filename_dot}'")
        return G # Zwracamy obiekt grafu
    except Exception as e:
        print(f"Błąd podczas renderowania grafu Graphviz: {e}")
        print("Upewnij się, że Graphviz jest zainstalowany i dostępny w ścieżce systemowej (PATH).")
        return None


# --- Implementacja Algorytmu Alpha (Uproszczonego) ---

def calculate_alpha_relations(workflow_log, all_activities):
    """Oblicza relacje Alpha: >, ->, ||, # oraz zbiory start/end."""
    direct_succession = defaultdict(set)  # x > y
    footprint_matrix = defaultdict(lambda: defaultdict(str)) # Przechowuje relacje ->, ||, #

    # 1. Oblicz bezpośrednie następstwo (>)
    for trace in workflow_log:
        for i in range(len(trace) - 1):
            direct_succession[trace[i]].add(trace[i+1])

    # 2. Oblicz relacje ->, ||, # (Footprint Matrix)
    causality = defaultdict(set) 
    parallel = set()           

    activities_list = sorted(list(all_activities)) # Dla deterministycznej kolejności
    for act_a in activities_list:
        for act_b in activities_list:
            a_follows_b = act_b in direct_succession.get(act_a, set())
            b_follows_a = act_a in direct_succession.get(act_b, set())

            if a_follows_b and not b_follows_a:
                footprint_matrix[act_a][act_b] = "->"
                causality[act_a].add(act_b)
            elif not a_follows_b and b_follows_a:
                footprint_matrix[act_a][act_b] = "<-"
                # Nie potrzebujemy <- explicite dla dalszych kroków, ale causality wystarczy
            elif a_follows_b and b_follows_a:
                footprint_matrix[act_a][act_b] = "||"
               
                if (act_a, act_b) not in parallel and (act_b, act_a) not in parallel:
                     parallel.add((act_a, act_b))
                     parallel.add((act_b, act_a)) # Jak w przykładzie
            else: 
                footprint_matrix[act_a][act_b] = "#"

    # 3. Oblicz zbiory Start (T_start) i End (T_end)
    start_events = set()
    end_events = set()
    if workflow_log:
        start_events = {trace[0] for trace in workflow_log if trace}
        end_events = {trace[-1] for trace in workflow_log if trace}

    # T_start = {a in all_activities | not exists b such that b -> a or b || a}
    # T_end = {a in all_activities | not exists b such that a -> b or a || b}
    formal_start_events = all_activities.copy()
    formal_end_events = all_activities.copy()
    for act_a in all_activities:
        for act_b in all_activities:
             if act_a == act_b: continue
             # Czy coś prowadzi do act_a?
             if footprint_matrix[act_b][act_a] in ["->", "||"]:
                 formal_start_events.discard(act_a)
             # Czy act_a prowadzi do czegoś?
             if footprint_matrix[act_a][act_b] in ["->", "||"]:
                 formal_end_events.discard(act_a)

    start_set_events = formal_start_events
    end_set_events = formal_end_events

    # 4. Oblicz odwróconą przyczynowość (pomocnicze dla bramek scalających)
    inv_causality = defaultdict(set)
    for source, targets in causality.items():
        for target in targets:
            inv_causality[target].add(source)

    print("Relacje Alpha obliczone.")

    return causality, parallel, start_set_events, end_set_events, inv_causality


# Klasa MyGraph (z niewielkimi modyfikacjami dla unikalności nazw bramek)
class MyGraph(graphviz.Digraph):
    def __init__(self, *args, **kwargs):
        super(MyGraph, self).__init__(*args, **kwargs)
        self.graph_attr['rankdir'] = 'LR'
        self.node_attr['shape'] = 'box' 
        self.node_attr['style'] = 'rounded'
        self.graph_attr['nodesep'] = '0.6' 
        self.edge_attr.update(penwidth='1.5') 
        self._gateway_count = 0 # Licznik do tworzenia unikalnych nazw bramek

    def _unique_gateway_name(self, prefix, hint=""):
        self._gateway_count += 1
        return f"{prefix}_{self._gateway_count}_{hint}"

    def add_activity(self, name, **kwargs):
         merged_attrs = {'shape': 'box', 'style': 'rounded,filled', 'fillcolor': '#FFFFCC'}
         merged_attrs.update(kwargs)
         super(MyGraph, self).node(name, **merged_attrs)


    def add_event(self, name, **kwargs):
        # Zdarzenia startowe/końcowe
        merged_attrs = {'shape': 'circle', 'label': '', 'width': '0.3', 'fixedsize': 'true'}
        if 'start' in name.lower():
             merged_attrs.update({'fillcolor': '#90EE90', 'style': 'filled'}) # Zielony start
        elif 'end' in name.lower():
             merged_attrs.update({'shape': 'doublecircle', 'fillcolor': '#FFB6C1', 'style': 'filled'}) # Różowy/Czerwony koniec
        merged_attrs.update(kwargs)
        super(MyGraph, self).node(name, **merged_attrs)

    def add_gateway(self, name, label, **kwargs):
         # Bramki (XOR lub AND)
         merged_attrs = {
             'shape': 'diamond',
             'width': '.5', 'height': '.5', 
             'fixedsize': 'true',
             'fontsize': '20', 
             'label': label,
             'style': 'filled',
             'fillcolor': '#E0E0E0' 
             }
         merged_attrs.update(kwargs)
         super(MyGraph, self).node(name, **merged_attrs)

    def add_and_gateway(self, name, **kwargs):
        self.add_gateway(name, '+', **kwargs)

    def add_xor_gateway(self, name, **kwargs):
        self.add_gateway(name, '×', **kwargs) # 'x' lub '×'

    def add_split_gateway(self, source, targets, gateway_type, parallel_rel, *args):
        hint = f"{source}->{'_'.join(sorted(list(targets)))}" # Sortowanie dla spójności nazwy
        is_parallel_split = False

        if len(targets) > 1:
             target_list = sorted(list(targets))
             
             is_parallel_split = any((t1, t2) in parallel_rel for i, t1 in enumerate(target_list) for t2 in target_list[i+1:])


        gateway_name = self._unique_gateway_name(f"{gateway_type}s", hint)

        if gateway_type == "AND" or (gateway_type == "AUTO" and is_parallel_split):
            self.add_and_gateway(gateway_name, *args)
        else: # XOR or AUTO and not parallel
            self.add_xor_gateway(gateway_name, *args)

        super(MyGraph, self).edge(source, gateway_name)
        for target in targets:
            super(MyGraph, self).edge(gateway_name, target)
        return gateway_name # Zwracamy nazwę utworzonej bramki

    def add_merge_gateway(self, sources, target, gateway_type, parallel_rel, *args):
        hint = f"{'_'.join(sorted(list(sources)))}->{target}"
        is_parallel_merge = False
        # Podobnie jak przy split, sprawdzamy relacje MIĘDZY źródłami ('sources')
        if len(sources) > 1:
            source_list = sorted(list(sources))
            is_parallel_merge = any((s1, s2) in parallel_rel for i, s1 in enumerate(source_list) for s2 in source_list[i+1:])

        gateway_name = self._unique_gateway_name(f"{gateway_type}m", hint)

        if gateway_type == "AND" or (gateway_type == "AUTO" and is_parallel_merge):
            self.add_and_gateway(gateway_name, *args)
        else: # XOR or AUTO and not parallel
            self.add_xor_gateway(gateway_name, *args)

        super(MyGraph, self).edge(gateway_name, target)
        for source in sources:
            super(MyGraph, self).edge(source, gateway_name)
        return gateway_name


def generate_bpmn_graph(causality, parallel, start_events, end_events, inv_causality, all_activities, filename_base):
    """Generuje graf BPMN na podstawie relacji Alpha."""
    G = MyGraph(comment='Alpha Miner BPMN')

    processed_sources_for_split = set()
    processed_targets_for_merge = set()
    edges_to_add = set() # Przechowuje krawędzie 1-do-1

    # 1. Dodaj wszystkie Aktywności
    for activity in all_activities:
        G.add_activity(activity)

    # 2. Dodaj Bramki Rozdzielające (Split)
    for source, targets in causality.items():
        if len(targets) > 1:
            # Używamy 'AUTO' do automatycznego wyboru XOR/AND na podstawie relacji równoległości między celami
            # Potrzebujemy jednak przekazać `parallel` do funkcji
            G.add_split_gateway(source, targets, "AUTO", parallel)
            processed_sources_for_split.add(source)
        elif len(targets) == 1:
            # Zapisz krawędź 1-do-1 do dodania później
            target = list(targets)[0]
            edges_to_add.add((source, target))

    # 3. Dodaj Bramki Scalające (Merge)
    for target, sources in inv_causality.items():
        if len(sources) > 1:
            G.add_merge_gateway(sources, target, "AUTO", parallel)
            processed_targets_for_merge.add(target)
            
            for source in sources:
                 edges_to_add.discard((source, target))
        
    # 4. Dodaj pozostałe krawędzie 1-do-1 (które nie były częścią bramek)
    for source, target in edges_to_add:
             G.edge(source, target)

    # 5. Dodaj Zdarzenia Startowe
    G.add_event("start")
    if len(start_events) > 1:
        # Sprawdź relacje między zdarzeniami startowymi
        G.add_split_gateway("start", start_events, "AUTO", parallel)
    elif len(start_events) == 1:
        G.edge("start", list(start_events)[0])
    
    # 6. Dodaj Zdarzenia Końcowe
    G.add_event("end")
    if len(end_events) > 1:
        
        G.add_merge_gateway(end_events, "end", "AUTO", parallel)
    elif len(end_events) == 1:
        G.edge(list(end_events)[0], "end")
    

    # Zapis i renderowanie
    try:
        output_filename_dot = f"{filename_base}.gv"
        output_filename_png = f"{filename_base}.png"
        G.render(output_filename_dot, view=False, format='png', outfile=output_filename_png) # Zapisuje .gv i .png
        print(f"Graf BPMN (Alpha) zapisany jako '{output_filename_png}' i '{output_filename_dot}'")
        return G
    except Exception as e:
        print(f"Błąd podczas renderowania grafu BPMN Graphviz: {e}")
        print("Upewnij się, że Graphviz jest zainstalowany i dostępny w ścieżce systemowej (PATH).")
        return None

# --- Główna Logika Skryptu ---

if __name__ == "__main__":
    if MINER_TYPE == 'heuristic':
        print("\n--- Generowanie Grafu Heurystycznego ---")
        print(f"Próg częstotliwości aktywności: {ACTIVITY_FREQUENCY_THRESHOLD}")
        print(f"Próg częstotliwości przejść: {TRANSITION_FREQUENCY_THRESHOLD}")
        heuristic_graph = generate_heuristic_graph(
            activity_counter,
            transition_counter,
            direct_succession_rel,
            ACTIVITY_FREQUENCY_THRESHOLD,
            TRANSITION_FREQUENCY_THRESHOLD,
            OUTPUT_HEURISTIC_BASE
        )


    elif MINER_TYPE == 'alpha':
        print("\n--- Generowanie Grafu BPMN (Algorytm Alpha) ---")
        causality, parallel, start_events, end_events, inv_causality = calculate_alpha_relations(
            workflow_log,
            all_activities
        )
        bpmn_graph = generate_bpmn_graph(
            causality,
            parallel,
            start_events,
            end_events,
            inv_causality,
            all_activities,
            OUTPUT_BPMN_BASE
        )

    else:
        print(f"Nieznany typ minera: '{MINER_TYPE}'. Wybierz 'heuristic' lub 'alpha'.")

    print("\n--- Zakończono ---")