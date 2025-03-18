from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from random import randint
from random import sample
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.graphics import Color
from kivy.graphics import Line

KV = '''
<MainLayout>:
    orientation: 'vertical'
    BoxLayout:
        id: word_lyt
        orientation: 'vertical'
    Label:
        size_hint: 1, 0.2
        text: root.cur_text
        canvas.before:
            Color:
                rgb: 0.8, 0.8, 0.8
            Rectangle:
                size: self.size[0], self.size[1] * 0.02
                pos: self.pos
            Rectangle:
                size: self.size[0], self.size[1] * 0.02
                pos: 0, self.pos[1] + self.height - (self.size[1] * 0.02)
    GridLayout:
        id: grid_lyt
        rows: root.rows
        cols: root.cols
        canvas.after:
            Color:
                rgba: 1.0, 1.0, 1.0, 0.5
            Line:
                points: root.points
                width: 10
            Line:
                points: root.points2
                width: root.line_width
                
<WordLabel>:
'''

Builder.load_string(KV)

ASCII_MIN = 97
ASCII_MAX = 122
FILENAME = "words_en.txt"
SIZE = (15, 10) # cols, rows
MATCH_COLOR = (0, 0.3, 0.5) # R: 0 G: 77 B: 128
WORD_QNT = 10

class WordLabel(Label):
    placed = False
    x_y = ()
    
    def __init__(self, app, pos, **kwargs):
        super(WordLabel, self).__init__(**kwargs)
        
        self.app = app
        self.x_y = tuple((pos[0], pos[1]))
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.app.touch_count == 1:
                self.app.ml.cur_text = f"{self.text}"
                self.app.first_sel = self
                
        super(WordLabel, self).on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            if self.app.touch_count == 1:
                if self.app.first_sel is not None and self.app.first_sel != self and self.app.last_sel != self:
                    self.app.last_sel = self
                    self.app.try_paint()
                
        super(WordLabel, self).on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if self.app.touch_count == 0:
            self.app.first_sel = None
            self.app.last_sel = None
        
        super(WordLabel, self).on_touch_up(touch)

class MainLayout(BoxLayout):
    rows = NumericProperty(SIZE[1])
    cols = NumericProperty(SIZE[0])
    line_width = NumericProperty(1)
    line_width_set = False
    cur_text = StringProperty("")
    points = ListProperty([])
    points2 = ListProperty([])

    def __init__(self, app, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        
        self.app = app
        
    def on_touch_down(self, touch):
        if not self.line_width_set:
            self.line_width = (self.width / (self.cols if self.cols > self.rows else self.rows)) / 2
            self.line_width_set = True
        
        self.app.touch_count += 1
        
        super(MainLayout, self).on_touch_down(touch)
        
    def on_touch_move(self, touch):
        fs = self.app.first_sel
        if fs is not None:
            pos_x = fs.pos[0] + (fs.width / 2)
            pos_y = fs.pos[1] + (fs.height / 2)
            point1 = (pos_x, pos_y)
            self.points = [point1, touch.pos]
        
        super(MainLayout, self).on_touch_move(touch)
        
    def on_touch_up(self, touch):
        self.app.touch_count -= 1
        
        self.cur_text = ""
        self.points = []
        self.points2 = []
        
        super(MainLayout, self).on_touch_up(touch)


def is_line_or_diagonal(pos1, pos2):
     if pos1[0] == pos2[0]:
         return True

     if pos1[1] == pos2[1]:
         return True

     if abs(pos1[0] - pos2[0]) == abs(pos1[1] - pos2[1]):
         return True

     return False

class MyApp(App):
    array = []
    words = []
    touch_count = 0
    first_sel = None
    last_sel = None
    
    def __init__(self, **kwargs):
        super(MyApp, self).__init__(**kwargs)
        
        self.ml = MainLayout(self)
        self.setup_matrix(SIZE)
        self.setup_game()
  
    def try_paint(self):
        pos_first = self.first_sel.x_y
        pos_last = self.last_sel.x_y
        if is_line_or_diagonal(pos_first, pos_last):
            self.ml.cur_text = ""
            
            point1 = (self.first_sel.pos[0] + (self.first_sel.width / 2), self.first_sel.pos[1] + (self.first_sel.height / 2))
            point2 = (self.last_sel.pos[0] + (self.last_sel.width / 2), self.last_sel.pos[1] + (self.last_sel.height / 2))
            self.ml.points2 = (point1, point2)
            
            step_x = 0
            step_y = 0
            if pos_first[0] > pos_last[0]:
                step_x = -1
            elif pos_first[0] < pos_last[0]:
                step_x = 1
            if pos_first[1] > pos_last[1]:
                step_y = -1
            elif pos_first[1] < pos_last[1]:
                step_y = 1
                
            x = pos_first[0]
            y = pos_first[1]
            
            while True:
                self.ml.cur_text += self.array[x][y].text
        
                if self.array[x][y] == self.last_sel:
                    break
                    
                y += step_y
                x += step_x
                
            for word in self.words:
                if self.ml.cur_text.casefold() == word.text.casefold() and not "[/s]" in self.ml.cur_text:
                    word.text = f"[s]{word.text}[/s]"
                    with self.ml.canvas.before:
                        Color(rgb=MATCH_COLOR)
                        Line(points=self.ml.points2, width=(self.ml.width / (self.ml.cols if self.ml.cols > self.ml.rows else self.ml.rows)) / 2)

    def setup_matrix(self, size):
        for x in range(size[1]):
            inner_array = []
            for y in range(size[0]):
                char = randint(ASCII_MIN, ASCII_MAX)
                wid = WordLabel(self, (x, y), text=chr(char).upper())
                inner_array.append(wid)
                self.ml.ids.grid_lyt.add_widget(wid)
            self.array.append(inner_array)
        
    def setup_game(self):
        wl = self.ml.ids.word_lyt
        
        selected_words = list()
        lines = list(set(line.casefold().strip() for line in open(FILENAME)))
        word = ""
        current_word_qnt = 0
        
        while current_word_qnt < WORD_QNT:
            cur_labels_list = []
            cur_w_list = []
            found_word = True
            while True:
                desired_length = randint(4, 9)
                cur_len = 0
                direction = randint(0, 3)
                rev = (randint(0, 1) == 1)
                start_col = 0
                start_row = 0
                step_x = 0
                step_y = 0
                
                if direction == 0:
                    # horizontal —
                    start_row = randint(0, SIZE[1] - 1)
                    step_y = 0
                    if rev:
                        # reversed
                        start_col = randint(desired_length - 1, SIZE[0] - 1)
                        step_x = - 1
                    else:
                        start_col = randint(0, SIZE[0] - desired_length)
                        step_x = 1
                elif direction == 1:
                    # vertical |
                    start_col = randint(0, SIZE[0] - 1)
                    step_x = 0
                    if rev:
                        # reversed
                        start_row = randint(desired_length - 1, SIZE[1] - 1)
                        step_y = -1
                    else:
                        start_row = randint(0, SIZE[1] - desired_length)
                        step_y = 1
                elif direction == 2:
                    # diagonal right /
                    if rev:
                        # reversed
                        start_row = randint(0, SIZE[1] - desired_length)
                        start_col = randint(desired_length - 1, SIZE[0] - 1)
                        step_x = -1
                        step_y = 1
                    else:
                        start_row = randint(desired_length - 1, SIZE[1] - 1)
                        start_col = randint(0, SIZE[0] - desired_length)
                        step_x = 1
                        step_y = -1
                elif direction == 3:
                    # diagonal left \
                    if rev:
                        # reversed
                        start_row = randint(desired_length - 1, SIZE[1] - 1)
                        start_col = randint(desired_length - 1, SIZE[0] - 1)
                        step_x = -1
                        step_y = -1
                    else:
                        start_row = randint(0, SIZE[1] - desired_length)
                        start_col = randint(0, SIZE[0] - desired_length)
                        step_x = 1
                        step_y = 1
                        
                row = start_row
                col = start_col
                
                str_eval = f"list(line for line in lines if len(line) == {desired_length}"
                
                for x in range(desired_length):
                    cur_lbl = self.array[row][col]
                    cur_len += 1
                    if cur_lbl.placed:
                        str_eval = f"{str_eval} and line[{x}] == '{cur_lbl.text.casefold()}'"
                    col += step_x
                    row += step_y
                
                str_eval = f"{str_eval})"
                new_lines = eval(str_eval)
                    
                if len(new_lines) == 0:
                    found_word = False
                    break
                    
                word = str(sample(new_lines, 1)[0])
                lines.remove(word)
                
                row = start_row
                col = start_col
                for x in range(desired_length):
                    cur_lbl = self.array[row][col]
                    cur_len += 1
                    letter = word[x].upper()
                    if not cur_lbl.placed or (cur_lbl.placed and cur_lbl.text == letter):
                        cur_labels_list.append(cur_lbl)
                        cur_w_list.append(letter)
                    else:
                        cur_len = 0
                        break
                    col += step_x
                    row += step_y
                    
                if cur_len >= len(word):
                    break
                    
            if found_word:
                selected_words.append(word.upper())
                for x in range(len(cur_labels_list)):
                    cur_labels_list[x].text = cur_w_list[x].upper()
                    cur_labels_list[x].placed = True
                    
                current_word_qnt += 1
                
        selected_words.sort()
        for word in selected_words:
            lbl = Label(text=word, markup=True)
            wl.add_widget(lbl)
            self.words.append(lbl)
            
    def build(self):
        return self.ml

if __name__ == "__main__":
    MyApp().run()
