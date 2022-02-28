'''
(descriptions)
'''

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation as manimation


class GameOfLife:
    def __init__(self, lattice):
        self.lattice = lattice
        self.xlen = lattice.shape[1]
        self.ylen = lattice.shape[0]
        self.n = self.xlen * self.ylen
        self.alive_cells = 0
        for i in range(len(self.lattice)):
            for j in range(len(self.lattice[0])):
                if self.lattice[i, j] == 1:
                    self.alive_cells += 1
        self.cm = None  # center of mass

    def update(self, i, j, updates):
        alive_neighs = 0
        # Chekc all 8 neighbours
        for delta in [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]:
            neigh_y, neigh_x = i + delta[0], j + delta[1]
            # Check boundaries
            if neigh_x >= self.xlen:
                neigh_x = 0
            elif neigh_x < 0:
                neigh_x = self.xlen - 1
            if neigh_y >= self.ylen:
                neigh_y = 0
            elif neigh_y < 0:
                neigh_y = self.ylen - 1
            # Check is neighbour alive
            if self.lattice[neigh_y, neigh_x] == 1:
                alive_neighs += 1
        # Mark new updates
        if self.lattice[i, j] == 1:
            if alive_neighs < 2:
                updates[(i, j)] = 0
                self.alive_cells -= 1
            elif alive_neighs > 3:
                updates[(i, j)] = 0
                self.alive_cells -= 1
        else:
            if alive_neighs == 3:
                updates[(i, j)] = 1
                self.alive_cells += 1

    def sweep(self):
        # Get updates for every cell
        updates = {}
        for i in range(len(self.lattice)):
            for j in range(len(self.lattice)):
                self.update(i, j, updates)
        # Update the cell in the lattice
        for k in updates.keys():
            self.lattice[k[0], k[1]] = updates[k]

    def run(self, steps, rec_weight=False, print_progress=True):
        weight_rec = None
        if rec_weight:
            weight_rec = [self.alive_cells]
        for i in range(steps):
            self.sweep()
            if rec_weight:
                weight_rec.append(self.alive_cells)
            if print_progress:
                print('Done ' + str(i + 1) + '/' + str(steps))
        return weight_rec

    def center_of_mass(self):
        '''
        Return r_cm = x_cm, y_cm

        Question: How to do this more efficiently (locally)? -> do that while updating all cells(??)
        '''
        r_sum = [0, 0]
        for i in range(len(self.lattice)):
            for j in range(len(self.lattice[0])):
                if self.lattice[i, j] == 1:
                    r_sum[0] += j  # j <-> x-coordinate
                    r_sum[1] += i  # i <-> y-coordinate
        r_sum[0] = r_sum[0] / self.alive_cells
        r_sum[1] = r_sum[1] / self.alive_cells
        return (r_sum[0], r_sum[1])


class InitialSetUps:
    def check(xlen, ylen):
        '''
        Check that the lattice will be atleast 10x10
        (maybe less???)
        '''
        if xlen < 10:
            raise Exception('Do not have xlen < 10')
        if ylen < 10:
            raise Exception('Do not have ylen < 10')

    def get_random(xlen=50, ylen=50):
        return np.random.randint(0, 2, (ylen, xlen))

    def get_glider(xlen=50, ylen=50):
        InitialSetUps.check(xlen, ylen)
        lattice = np.zeros((ylen, xlen))
        lattice[2, 2] = 1
        lattice[3, 3] = 1
        lattice[4, 1] = 1
        lattice[4, 2] = 1
        lattice[4, 3] = 1
        return lattice

    def get_beehive(xlen=50, ylen=50):
        lattice = np.zeros((ylen, xlen))
        lattice[2, 3] = 1
        lattice[3, 2] = 1
        lattice[3, 4] = 1
        lattice[4, 2] = 1
        lattice[4, 4] = 1
        lattice[5, 3] = 1
        return lattice

    def get_oscillator(xlen=50, ylen=50):
        lattice = np.zeros((ylen, xlen))
        lattice[2, 2] = 1
        lattice[3, 2] = 1
        lattice[4, 2] = 1
        return lattice


class View:
    def __init__(self, cellular_automata):
        self.cellular_automata = cellular_automata

        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(self.cellular_automata.lattice, cmap='Greys')
        self.ani = None

    def run(self, interval):
        self.ani = manimation.FuncAnimation(self.fig, self.animate, interval=interval, blit=True)
        plt.show()

    def animate(self, frame):
        gol.sweep()
        print('Step:', frame)
        self.im.set_data(self.cellular_automata.lattice)
        return self.im,


def run_visualisation(lattice, interval):
    # For example 350 (ms between frames) is a good interval
    gol = GameOfLife(lattice)
    myView = View(gol)
    myView.run(interval)


def alive_cells_sim(runs, steps, xlen=50, ylen=50):
    # Get the weight (number of alive cell) for number of random initial lattices
    weight_dataset = []
    for i in range(runs):
        lattice = InitialSetUps.get_random(xlen, ylen)
        gol = GameOfLife(lattice)
        weight_data = gol.run(steps, rec_weight=True, print_progress=False)
        weight_dataset.append(weight_data)
        print('Run: ' + str(i + 1) + ' / ' + str(runs))
    # Plot each run
    for weight_data in weight_dataset:
        plt.plot(weight_data, 'r--', alpha=0.4)
    # Plot the mean weight of these runs
    mean_weight = []
    for step in range(steps):
        step_i_mean_weight = 0
        for run in range(runs):
            step_i_mean_weight += weight_dataset[run][step]
        step_i_mean_weight = step_i_mean_weight / runs
        mean_weight.append(step_i_mean_weight)
    plt.plot(mean_weight, 'r-')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    xlen, ylen = 50, 50
    lattice = InitialSetUps.get_random(xlen, ylen)
    gol = GameOfLife(lattice)
    steps = 200
    runs = 10
    alive_cells_sim(runs, steps)
