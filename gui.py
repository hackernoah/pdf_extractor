# adapted from https://github.com/dpapathanasiou/pdfminer-layout-scanner

from os.path import exists
from tempfile import mkdtemp, mkstemp
from shutil import rmtree
from binascii import b2a_hex
from os import write, close
from threading import Thread

from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import (
    LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTChar, LTCurve,
    LTLine, LTRect,
)

from kivy.lang import Builder
from kivy.clock import Clock

from kivy.graphics import Mesh, Color
from kivy.graphics.tesselator import Tesselator

from kivy.uix.widget import Widget
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.properties import (
    StringProperty, ListProperty, NumericProperty, AliasProperty,
    DictProperty, ObjectProperty, BooleanProperty, ColorProperty,
)

Builder.load_string('''
#:import RGBA kivy.utils.rgba
<PDFDocumentWidget>:
    viewclass: 'PDFPageWidget'
    key_size: 'size'
    # async load is buggy at the moment
    # async_load: True
    RecycleGridLayout:
        spacing: 5
        cols: root.cols
        rows: root.rows
        size_hint: None, None
        size: self.minimum_size
        default_size_hint: None, None
<PDFPageWidget>:
    size_hint: None, None
    canvas.before:
        Color:
            rgba: RGBA('FFFFFF')
        Rectangle:
            size: self.size
<PDFLabelWidget,PDFImageWidget>:
    size_hint: None, None
<PDFImageWidget>:
    pos: self.bbox[:2]
    size: self.bbox[2] - self.x, self.bbox[3] - self.y
<PDFLabelWidget>:
    text_size: self.width, None
    height: self.texture_size[1]
    color: RGBA('000000')
    font_size: 8
<PDFCurveWidget>:
''')


class PDFDocumentWidget(RecycleView):
    source = StringProperty()
    password = StringProperty()
    cols = NumericProperty(None)
    rows = NumericProperty(None)
    _toc = ListProperty()
    async_load = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(PDFDocumentWidget, self).__init__(**kwargs)
        self._fp = None
        self._document = None
        self._tmpdir = None
        self.bind(source=self.load)
        if self.source:
            self.load()

    def load(self, *args):
        if self._fp:
            # close the previous pdf file
            self._fp.close()

        pdf_doc = self.source
        data = []
        if not pdf_doc or not exists(pdf_doc):
            self.pages = []
            self._doc = []
            self._document = None
            if self._tmpdir:
                rmtree(self._tmpdir)
                self._tmpdir = None

        try:
            # open the pdf file
            self._fp = fp = open(pdf_doc, 'rb')
            # create a parser object associated with the file object
            parser = PDFParser(fp)
            # create a PDFDocument object that stores the document structure
            doc = PDFDocument(parser)
            # connect the parser and document objects
            parser.set_document(doc)
            # supply the password for initialization
            # doc.initialize(self.password)

            # if doc.is_extractable:
            # apply the function and return the result
            self._document = doc
            self._parse_toc()
            self._create_tmpdir()
            self._parse_pages()
        except IOError as e:
            # the file doesn't exist or similar problem
            print(e)

    def _create_tmpdir(self):
        if not self._tmpdir:
            self._tmpdir = mkdtemp()
        return self._tmpdir

    def _parse_toc(self):
        """With an open PDFDocument object, get the table of contents (toc) data
        [this is a higher-order function to be passed to with_pdf()]"""
        toc = []
        doc = self._document
        try:
            outlines = doc.get_outlines()
            for (level, title, dest, a, se) in outlines:
                toc.append((level, title))
        except:
            pass
        finally:
            self._toc = toc

    def _parse_pages(self):
        doc = self._document
        if not doc:
            self.data = []
            return

        data = []

        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        self.device = device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        self.interpreter = PDFPageInterpreter(rsrcmgr, device)

        for i, page in enumerate(PDFPage.create_pages(doc)):
            p = {
                'manager': self,
                'page': page,
                'size': page.attrs.get('MediaBox', [0, 0, 0, 0])[2:],
            }
            data.append(p)
        self.data = data


class PDFImageWidget(Image):
    bbox = ListProperty([0, 0, 100, 100])


class PDFLabelWidget(Label):
    bbox = ListProperty([0, 0, 100, 100])


class PDFCurveWidget(Widget):
    points = ListProperty()
    line_width = NumericProperty()
    stroke = BooleanProperty(False)
    fill = BooleanProperty(False)
    even_odd = BooleanProperty()
    color = ColorProperty()
    fill_color = ColorProperty()

    def __init__(self, **kwargs):
        super(PDFCurveWidget, self).__init__(**kwargs)
        build = Clock.create_trigger(self.build, 0)

        self.bind(
            points=build,
            line_width=build,
            stroke=build,
            fill=build,
            even_odd=build,
            color=build,
            fill_color=build
        )

    def build(self, *args):
        self.canvas.clear()
        if not self.points:
            return

        with self.canvas:
            if self.fill:
                Color(rgba=self.fill_color)
                t = Tesselator()
                t.add_contour(self.points)
                if tess.tesselate:
                    for vertices, indices in tess.meshes:
                        Mesh(
                            vertices=vertices,
                            indices=indices,
                            mode='triangle fan'
                        )
                else:
                    print("mesh didn't tesselate!")

            if self.stroke:
                Color(rgba=self.color)
                Line(
                    points=self.points,
                    width=self.line_width
                )


class PDFPageWidget(RelativeLayout):
    labels = DictProperty()
    attributes = DictProperty()
    manager = ObjectProperty()
    page = ObjectProperty()
    items = ListProperty()

    def on_page(self, *args):
        if self.manager.async_load:
            Thread(target=self._load_page).start()
        else:
            self._load_page()

    def _load_page(self):
        self.manager.interpreter.process_page(self.page)
        self.items = self.manager.device.get_result()

    def on_items(self, *args):
        self.clear_widgets()
        self._render_content(self.items)

    def _render_content(self, lt_objs):
        """Iterate through the list of LT* objects and capture the text
        or image data contained in each
        """
        for lt_obj in lt_objs:
            print(lt_obj)
            if isinstance(lt_obj, LTChar):
                self.add_text(
                    text=lt_obj.get_text(),
                    box_pos=(lt_obj.x0, lt_obj.y0),
                    box_size=(lt_obj.width, lt_obj.height),
                    # font_size=lt_obj.fontsize,
                    # font_name=lt_obj.fontname,
                )

            elif isinstance(lt_obj, (LTTextBox, LTTextLine)):
                # text, so arrange is logically based on its column width
                # this way is very limited style wise, and doesn't allow
                # support for font, color, style, etc management, as
                # pdfminer doesn't provide these information at text box
                # level, by using the following nested loop, it's
                # possible to have font family info, but for individual
                # character, which is impractical to create direct
                # labels for.
                # for obj in lt_obj:
                #     print(obj)
                #     for o in obj:
                #         print(o)

                self.add_text(
                    text=lt_obj.get_text(),
                    box_pos=(lt_obj.x0, lt_obj.y0),
                    box_size=(lt_obj.width, lt_obj.height),
                )

            elif isinstance(lt_obj, LTImage):
                saved_file = self.save_image(lt_obj)
                if saved_file:
                    self.add_widget(
                        PDFImageWidget(
                            source=saved_file,
                            bbox=lt_obj.bbox
                        )
                    )

            elif isinstance(lt_obj, LTFigure):
                self._render_content(lt_obj)

            # all of these are actually LTCurves, but all types here for
            # clarity
            elif isinstance(lt_obj, (LTLine, LTRect, LTCurve)):
                self.add_widget(
                    PDFCurveWidget(
                        points=lt_obj.pts or [],
                        line_width=lt_obj.linewidth or 1.0,
                        stroke=lt_obj.stroke,
                        fill=lt_obj.fill,
                        even_odd=lt_obj.evenodd,
                        # colors seem to be indices, to some dict i
                        # can't find in what pdfminer exposes
                        color='#FFFFFFFF', # lt_obj.stroking_color or 
                        fill_color='#00000000' # lt_obj.non_stroking_color or 
                    )
                )

    def save_image(self, lt_image):
        """Try to save the image data from this LTImage object, and
        return the file name, if successful
        """
        if lt_image.stream:
            file_stream = lt_image.stream.get_rawdata()
            if file_stream:
                file_ext = self.determine_image_type(file_stream[0:4])
                if file_ext:
                    fd, fn = mkstemp(dir=self.manager._tmpdir, suffix='.{}'.format(file_ext))
                    write(fd, file_stream)
                    close(fd)
                    return fn

    @staticmethod
    def determine_image_type(stream_first_4_bytes):
        """Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
        file_type = None
        bytes_as_hex = b2a_hex(stream_first_4_bytes)
        if bytes_as_hex.startswith(b'ffd8'):
            file_type = '.jpeg'
        elif bytes_as_hex == b'89504e47':
            file_type = '.png'
        elif bytes_as_hex == b'47494638':
            file_type = '.gif'
        elif bytes_as_hex.startswith(b'424d'):
            file_type = '.bmp'
        return file_type

    def add_text(self, text, box_pos, box_size, **kwargs):
        label = self.labels.get((box_pos, box_pos))
        if not label:
            label = PDFLabelWidget(text=text, pos=box_pos, size=box_size, **kwargs)
            self.labels[(box_pos, box_size)] = label
            self.add_widget(label)
        else:
            label.text += text

    def add_image(self, lt_image):
        source = self.save_image(lt_image)
        if source:
            image = PDFImageWidget(
                source=source,
                pos=(lt_image.x0, lt_image.y0),
                size=(lt_image.widt, lt_image.height)
            )
            self.add_widget(image)
            self.images.append(image)


if __name__ == '__main__':
    from sys import argv
    from kivy.base import runTouchApp
    from kivy.uix.scrollview import ScrollView

    if len(argv) > 1:
        fn = argv[1]
    else:
        fn = 'example.pdf'
    root = PDFDocumentWidget(source=fn, cols=1)
    runTouchApp(root)