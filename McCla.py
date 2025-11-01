class QuineMcCluskey:
    def __init__(self, num_variables, minterms, dont_cares=None):
        
        self.num_variables = num_variables
        self.minterms = sorted(set(minterms))
        self.dont_cares = sorted(set(dont_cares)) if dont_cares else []
        self.all_terms = sorted(set(self.minterms + self.dont_cares))
        self.variable_names = [chr(65 + i) for i in range(num_variables)] 

    def decimal_to_binary(self, num):
        return format(num, f'0{self.num_variables}b')

    def count_ones(self, binary_str):
        return binary_str.count('1')

    def compare_terms(self, term1, term2):
        diff_count = 0
        diff_pos = -1

        for i in range(len(term1)):
            if term1[i] != term2[i]:
                if term1[i] == '-' or term2[i] == '-':
                    return None
                diff_count += 1
                diff_pos = i

        if diff_count == 1:
            combined = list(term1)
            combined[diff_pos] = '-'
            return ''.join(combined)
        return None

    def group_by_ones(self, terms_dict):
        groups = {}
        for term, minterms in terms_dict.items():
            ones = self.count_ones(term)
            if ones not in groups:
                groups[ones] = {}
            groups[ones][term] = minterms
        return groups

    def combine_terms(self, groups):
        new_terms = {}
        used_terms = set()

        sorted_groups = sorted(groups.keys())

        for i in range(len(sorted_groups) - 1):
            group1 = groups[sorted_groups[i]]
            group2 = groups[sorted_groups[i + 1]]

            for term1, mints1 in group1.items():
                for term2, mints2 in group2.items():
                    combined = self.compare_terms(term1, term2)
                    if combined:
                        new_minterms = tuple(sorted(set(mints1 + mints2)))
                        new_terms[combined] = new_minterms
                        used_terms.add(term1)
                        used_terms.add(term2)

        prime_implicants = {}
        for group in groups.values():
            for term, mints in group.items():
                if term not in used_terms:
                    prime_implicants[term] = mints

        return new_terms, prime_implicants

    def find_prime_implicants(self):
        current_terms = {}
        for term in self.all_terms:
            binary = self.decimal_to_binary(term)
            current_terms[binary] = (term,)

        all_prime_implicants = {}
        column = 1

        print("=" * 80)
        print(f"PASO 1: AGRUPACIÓN INICIAL POR NÚMERO DE 1's")
        print("=" * 80)

        groups = self.group_by_ones(current_terms)
        for group_num in sorted(groups.keys()):
            print(f"\nGrupo {group_num} ({group_num} unos):")
            for term, mints in sorted(groups[group_num].items()):
                mints_str = ','.join(map(str, mints))
                print(f"  {term}  →  m({mints_str})")
        while current_terms:
            print("\n" + "=" * 80)
            print(f"COLUMNA {column}: COMBINACIÓN DE TÉRMINOS")
            print("=" * 80)

            groups = self.group_by_ones(current_terms)
            new_terms, prime_imps = self.combine_terms(groups)

            if new_terms:
                print(f"\nNuevos términos combinados:")
                for term, mints in sorted(new_terms.items()):
                    mints_str = ','.join(map(str, mints))
                    print(f"  {term}  →  m({mints_str})")
            else:
                print("\nNo se pueden combinar más términos")

            if prime_imps:
                print(f"\nImplicantes primos encontrados en esta columna:")
                for term, mints in sorted(prime_imps.items()):
                    mints_str = ','.join(map(str, mints))
                    print(f"  {term}  →  m({mints_str}) ✓")
                all_prime_implicants.update(prime_imps)

            current_terms = new_terms
            column += 1

            if not new_terms:
                break

        return all_prime_implicants

    def create_prime_implicant_chart(self, prime_implicants):
        print("\n" + "=" * 80)
        print("PASO 2: TABLA DE IMPLICANTES PRIMOS")
        print("=" * 80)

        # Crear tabla
        chart = {}
        for term, mints in prime_implicants.items():
            chart[term] = [m for m in mints if m in self.minterms]

        # Imprimir tabla
        print(f"\n{'Implicante Primo':<20} | Término | Cubre Mintérminos")
        print("-" * 70)

        for i, (term, covered) in enumerate(sorted(chart.items()), 1):
            algebraic = self.binary_to_algebraic(term)
            covered_str = ', '.join(map(str, covered))
            print(f"P{i:<2} {algebraic:<15} | {term:<8} | {covered_str}")

        return chart

    def binary_to_algebraic(self, binary_term):
        result = []
        for i, bit in enumerate(binary_term):
            if bit == '1':
                result.append(self.variable_names[i])
            elif bit == '0':
                result.append(self.variable_names[i] + "'")
        return ''.join(result) if result else "1"

    def find_essential_prime_implicants(self, chart):
        essential = {}
        covered_minterms = set()

        # Para cada mintérmino, contar cuántos implicantes lo cubren
        minterm_coverage = {m: [] for m in self.minterms}
        for term, covered in chart.items():
            for m in covered:
                minterm_coverage[m].append(term)

        # Implicantes esenciales: únicos que cubren un mintérmino
        print("\n" + "=" * 80)
        print("PASO 3: IDENTIFICAR IMPLICANTES PRIMOS ESENCIALES")
        print("=" * 80)

        for minterm, covering_terms in sorted(minterm_coverage.items()):
            if len(covering_terms) == 1:
                term = covering_terms[0]
                if term not in essential:
                    essential[term] = chart[term]
                    covered_minterms.update(chart[term])
                    algebraic = self.binary_to_algebraic(term)
                    print(f"✓ {algebraic:<15} ({term}) es ESENCIAL (único que cubre m{minterm})")

        if not essential:
            print("No hay implicantes primos esenciales únicos")

        return essential, covered_minterms

    def find_minimal_coverage(self, chart, essential, covered_minterms):
        remaining_minterms = set(self.minterms) - covered_minterms

        if not remaining_minterms:
            print("\n✓ Todos los mintérminos están cubiertos por implicantes esenciales")
            return {}

        print("\n" + "=" * 80)
        print("PASO 4: CUBRIR MINTÉRMINOS RESTANTES")
        print("=" * 80)
        print(f"\nMintérminos restantes: {sorted(remaining_minterms)}")

        # Selección greedy: elegir implicantes que cubran más términos restantes
        additional = {}
        remaining = set(remaining_minterms)

        while remaining:
            best_term = None
            best_coverage = 0

            for term, covered in chart.items():
                if term not in essential and term not in additional:
                    coverage_count = len(set(covered) & remaining)
                    if coverage_count > best_coverage:
                        best_coverage = coverage_count
                        best_term = term

            if best_term:
                additional[best_term] = chart[best_term]
                newly_covered = set(chart[best_term]) & remaining
                remaining -= newly_covered
                algebraic = self.binary_to_algebraic(best_term)
                print(f"+ Agregando {algebraic:<15} ({best_term}) - cubre {sorted(newly_covered)}")
            else:
                break

        return additional

    def minimize(self):
        print("\n" + "╔" + "=" * 78 + "╗")
        print("║" + " " * 15 + "MÉTODO DE QUINE-MCCLUSKEY" + " " * 38 + "║")
        print("╚" + "=" * 78 + "╝")

        print(f"\nNúmero de variables: {self.num_variables} ({', '.join(self.variable_names)})")
        print(f"Mintérminos: {self.minterms}")
        if self.dont_cares:
            print(f"Don't cares: {self.dont_cares}")

        prime_implicants = self.find_prime_implicants()

        chart = self.create_prime_implicant_chart(prime_implicants)

        essential, covered = self.find_essential_prime_implicants(chart)

        additional = self.find_minimal_coverage(chart, essential, covered)

        final_solution = {**essential, **additional}

        print("\n" + "╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "FUNCIÓN MINIMIZADA" + " " * 35 + "║")
        print("╚" + "=" * 78 + "╝")

        terms = []
        for term in sorted(final_solution.keys()):
            algebraic = self.binary_to_algebraic(term)
            terms.append(algebraic)

        function = ' + '.join(terms)
        print(f"\nF({','.join(self.variable_names)}) = {function}")

        print(f"\nNúmero de términos producto: {len(final_solution)}")
        print(f"Total de literales: {sum(t.count('1') + t.count('0') for t in final_solution.keys())}")

        return function, final_solution

def main():
    print("\n" + "█" * 80)
    print("█" + " " * 20 + "MINIMIZADOR QUINE-MCCLUSKEY" + " " * 32 + "█")
    print("█" * 80)

    print("\n\n【 EJEMPLO 1: DETECTOR DE NÚMEROS PRIMOS (5 bits) 】")
    print("-" * 80)

    qm1 = QuineMcCluskey(
        num_variables=5,
        minterms=[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    )
    function1, solution1 = qm1.minimize()

    print("\n\n" + "█" * 80)
    print("\n【 EJEMPLO 2: FUNCIÓN CON DON'T CARES (4 variables) 】")
    print("-" * 80)

    qm2 = QuineMcCluskey(
        num_variables=4,
        minterms=[0, 1, 2, 5, 6, 7, 8, 9, 14],
        dont_cares=[10, 11, 15]
    )
    function2, solution2 = qm2.minimize()

    print("\n\n" + "█" * 80)
    print("\n【 EJEMPLO 3: FUNCIÓN SIMPLE (3 variables) 】")
    print("-" * 80)

    qm3 = QuineMcCluskey(
        num_variables=3,
        minterms=[0, 2, 5, 7]
    )
    function3, solution3 = qm3.minimize()

    print("\n\n" + "█" * 80)
    print("\n【 EJEMPLO 4: FUNCIÓN GRANDE (8 variables) 】")
    print("-" * 80)

    qm4 = QuineMcCluskey(
        num_variables=8,
        minterms=[0, 1, 2, 3, 4, 8, 16, 32, 64, 128, 255, 254, 127] 
    )
    function4, solution4 = qm4.minimize()

    print("\n\n" + "█" * 80)
    print("█" + " " * 25 + "PROGRAMA FINALIZADO" + " " * 36 + "█")
    print("█" * 80 + "\n")


if __name__ == "__main__":
    main()