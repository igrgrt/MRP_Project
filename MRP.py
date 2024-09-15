import pandas as pd

class MRP:
    def __init__(self, produkty, bom, czas_realizacji, stan_poczatkowy, zapas_bezpieczenstwa, wielkosc_partii):
        self.produkty = produkty  # Lista wszystkich produktów
        self.bom = bom  # Struktura materiałowa (BoM) - zależności między produktami
        self.czas_realizacji = czas_realizacji  # Czas realizacji dla każdego produktu
        self.stan_poczatkowy = stan_poczatkowy  # Początkowy stan magazynowy
        self.zapas_bezpieczenstwa = zapas_bezpieczenstwa  # Minimalny poziom zapasu (zapas bezpieczeństwa)
        self.wielkosc_partii = wielkosc_partii  # Wielkości partii produkcji
        self.harmonogram = pd.DataFrame(columns=['Dzień', 'Produkt', 'Zapotrzebowanie', 'Planowana produkcja'])

    def oblicz_zapotrzebowanie(self, produkt, dzien, ilosc_wymagana):
        """
        Oblicz harmonogram produkcji dla produktu i jego komponentów (rekursywnie).
        """
        # Sprawdzenie bieżącego stanu magazynu i zapasu bezpieczeństwa
        dostepny_stan = self.stan_poczatkowy.get(produkt, 0)
        zapotrzebowanie_netto = max(0, ilosc_wymagana - dostepny_stan - self.zapas_bezpieczenstwa.get(produkt, 0))

        print(f"\n--- Przetwarzanie {produkt} ---")
        print(f"Dzień: {dzien}, Wymagana ilość: {ilosc_wymagana}, Dostępne: {dostepny_stan}, Zapas bezpieczeństwa: {self.zapas_bezpieczenstwa.get(produkt, 0)}")
        print(f"Zapotrzebowanie netto dla {produkt}: {zapotrzebowanie_netto}")

        if zapotrzebowanie_netto > 0:
            #Planowanie produkcji w partiach
            liczba_partii = (zapotrzebowanie_netto + self.wielkosc_partii.get(produkt, 1) - 1) // self.wielkosc_partii.get(produkt, 1)
            planowana_produkcja = liczba_partii * self.wielkosc_partii.get(produkt, 1)
            dzien_produkcji = max(0, dzien - self.czas_realizacji.get(produkt, 0))

            print(f"Planowana produkcja dla {produkt}: {planowana_produkcja} (Partie: {liczba_partii}, Wielkość partii: {self.wielkosc_partii.get(produkt, 1)})")
            print(f"Produkcja zaplanowana na dzień {dzien_produkcji}")

            #Dodanie planu produkcji do harmonogramu
            nowy_wiersz = pd.DataFrame({'Dzień': [dzien_produkcji], 'Produkt': [produkt],
                                        'Zapotrzebowanie': [ilosc_wymagana], 'Planowana produkcja': [planowana_produkcja]})
            self.harmonogram = pd.concat([self.harmonogram, nowy_wiersz], ignore_index=True)

            #Aktualizacja stanu magazynowego
            self.stan_poczatkowy[produkt] = dostepny_stan + planowana_produkcja
            print(f"Zaktualizowany stan magazynu dla {produkt}: {self.stan_poczatkowy[produkt]}")

            #Obliczanie zapotrzebowania na komponenty (BoM poziom 2)
            if produkt in self.bom:
                for komponent, ilosc_na_produkt in self.bom[produkt].items():
                    zapotrzebowanie_na_komponent = planowana_produkcja * ilosc_na_produkt
                    print(f"Komponent {komponent} wymagany do {produkt}: {zapotrzebowanie_na_komponent} (Ilość na produkt: {ilosc_na_produkt})")
                    self.oblicz_zapotrzebowanie(komponent, dzien_produkcji, zapotrzebowanie_na_komponent)
        else:
            print(f'{produkt} posiada wystarczający stan magazynowy.')

    def plan_mrp(self, zapotrzebowanie_produktow):
        """
        Planowanie MRP dla każdego zapotrzebowania na produkt w określonym dniu.
        """
        for produkt, (dzien, ilosc) in zapotrzebowanie_produktow.items():
            self.oblicz_zapotrzebowanie(produkt, dzien, ilosc)

        #Sortowanie według dnia produkcji
        self.harmonogram.sort_values(by='Dzień', inplace=True)
        return self.harmonogram


    def drukuj_koncowy_harmonogram(self):
        """
        Drukowanie ostatecznego harmonogramu produkcji w terminalu.
        """
        print("\n--- Ostateczny harmonogram produkcji ---")
        print(self.harmonogram.to_string(index=False))

#Definioweanie
#produktów i komponentów dla fotela (BoM)
produkty = ['Fotel', 'Rama', 'Nogi', 'Tkanina', 'Pianka']
bom = {
    'Fotel': {'Rama': 1, 'Nogi': 4, 'Tkanina': 3, 'Pianka': 2},  # 1 rama, 4 nogi, 3 metry tkaniny i 2 jednostki pianki na 1 fotel
}

#Czas realizacji w dniach dla każdego komponentu i produktu
czas_realizacji = {'Fotel': 5, 'Rama': 3, 'Nogi': 2, 'Tkanina': 1, 'Pianka': 1}

#Początkowy stan magazynowy dla produktów i komponentów
stan_poczatkowy = {'Fotel': 0, 'Rama': 10, 'Nogi': 40, 'Tkanina': 50, 'Pianka': 30}

#Definiowanie zapasu bezpieczeństwa
zapas_bezpieczenstwa = {'Fotel': 0, 'Rama': 5, 'Nogi': 10, 'Tkanina': 10, 'Pianka': 5}

#Definicja wielkości partii produkcji (np. 10 ram na partię)
wielkosc_partii = {'Fotel': 1, 'Rama': 10, 'Nogi': 20, 'Tkanina': 10, 'Pianka': 5}

#Tworzenie instancji MRP
mrp = MRP(produkty, bom, czas_realizacji, stan_poczatkowy, zapas_bezpieczenstwa, wielkosc_partii)

#Definicja zapotrzebowania na produkt (Dzień, Ilość)
zapotrzebowanie_produktow = {
    'Fotel': (10, 15)  # Potrzeba 15 foteli na dzień 10
}

#Planowanie MRP
harmonogram = mrp.plan_mrp(zapotrzebowanie_produktow)


#Wyświetlanie finalnego harmonogramu w terminalu
mrp.drukuj_koncowy_harmonogram()
