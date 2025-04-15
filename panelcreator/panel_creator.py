'''
PanelCreator class for creating panels of images with annotations.
Yuan-Ming Hsu (2024/11/26)
'''


from object_database import ObjectDatabase
from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class PanelCreator:

    def __init__(self, df, M, N, object_db):
        self.df: pd.DataFrame = df
        self.M: int = M
        self.N: int = N
        self.object_db: ObjectDatabase = object_db
        self.current_index = 0  # Tracks the current position in the dataframe

    def create(self, title_format=None, title_size=None, figsize=None, image_size=None,
               mark=True, scalebar=True, textboxs=None,
               show_now=False, random=False):
        M, N = self.M, self.N
        df = self.df
        panel_size = M * N
        self.panel_size = panel_size
        if random:
            # Shuffle or sample random rows
            df_subset = df.sample(n=panel_size)  # Random subset, 'random_state' for reproducibility
        else:
            # Select a sequential subset of the DataFrame
            df_subset = df.iloc[self.current_index:self.current_index + panel_size]
        num_objects = len(df_subset)

        if image_size is None:
            image_size = 2
        elif isinstance(image_size, (int, float)):
            if image_size <= 0:
                raise ValueError("image_size must be positive")
        else:
            raise ValueError("image_size must be a number")

        if figsize is None:
            ratio = min(min(image_size * N, 10) / N, min(image_size * M, 10) / M)
            figsize = (image_size * N, image_size * M)

        fig, axes = plt.subplots(M, N, figsize=figsize)
        axes = axes.flatten()  # Flatten axes array for easy indexing

        for i in range(panel_size):
            ax = axes[i]
            if i < num_objects:
                ######## Load the image ########
                index_fg = df_subset.iloc[i]['index_FG']
                image = self.object_db.get_image(index_fg)
                ################################
                ax.imshow(image)

                DEFAULT_PIXSCALE = 0.262 / 3600  # degree/pixel

                ######## Customize functionality ########
                if mark:
                    # Draw a dot at the center of the image
                    center_x = image.shape[1] // 2
                    center_y = image.shape[0] // 2
                    ax.plot(center_x, center_y, 'ro', markersize=2)

                    # Calculate the background object's location
                    dra = (df_subset.iloc[i]['Ra_BG'] - df_subset.iloc[i]['Ra_FG']) * \
                        np.cos(np.deg2rad(df_subset.iloc[i]['Dec_FG']))
                    ddec = (df_subset.iloc[i]['Dec_BG'] - df_subset.iloc[i]['Dec_FG'])

                    bg_x = center_x - dra / DEFAULT_PIXSCALE
                    bg_y = center_y - ddec / DEFAULT_PIXSCALE
                    ax.plot(bg_x, bg_y, 'bo', markersize=2)
                #########################################

                if scalebar:
                    SCALEBAR_LENGTH_ARCSEC = 2  # Length of the scalebar in arcseconds
                    scalebar_length_pixels = SCALEBAR_LENGTH_ARCSEC / (DEFAULT_PIXSCALE * 3600)  # Convert to pixels
                    MARGIN_LEFT = 3
                    MARGIN_BOTTOM = 3

                    # Draw the scalebar at the bottom-right corner
                    ax.plot(
                        [MARGIN_LEFT, MARGIN_LEFT + scalebar_length_pixels],
                        [image.shape[0] - MARGIN_BOTTOM, image.shape[0] - MARGIN_BOTTOM],
                        color='white', linewidth=2
                    )
                    ax.text(
                        MARGIN_LEFT + scalebar_length_pixels / 2,
                        image.shape[0] - MARGIN_BOTTOM - 2,
                        f'{SCALEBAR_LENGTH_ARCSEC}"',
                        color='white', fontsize=10, ha='center'
                    )

                values = df_subset.iloc[i].to_dict()
                if title_format:
                    title = title_format.format(**values)
                    if title_size:
                        ax.set_title(title, fontsize=title_size)
                    else:
                        ax.set_title(title)

                if textboxs:
                    for textbox in textboxs:
                        textbox.draw(ax, values)

                ax.axis('off')
            else:
                ax.axis('off')  # Blank space for remaining slots

        fig.set_layout_engine('compressed')

        if show_now:
            plt.show()
        return fig, axes

    def title(self, title: str, title_size=None):
        if title_size:
            plt.suptitle(title, fontsize=title_size)
        else:
            plt.suptitle(title)

    def next(self):
        if self.current_index + self.panel_size < len(self.df):
            self.current_index += self.panel_size
            # print(f"Current index: {self.current_index}")
            return True
        else:
            # print(f"Current index: {self.current_index}")
            return False

    def save_all(self, path, title=None, title_size=None, format_string=None, string_size=None,
                 figsize=None, image_size=None, mark=True, scalebar=True, textboxs=None, verbose=False):
        has_next = True
        while has_next:
            if verbose:
                print(f"Saving {path + f'{self.current_index:04}.png'}")
            fig, ax = self.create(figsize=figsize, title_format=format_string, title_size=string_size,
                                  image_size=image_size, mark=mark, scalebar=scalebar, textboxs=textboxs)
            if title is not None:
                if title_size:
                    fig.suptitle(title, fontsize=title_size)
                else:
                    fig.suptitle(title)
            fig.savefig(path + f'{self.current_index:04}.png', pad_inches='layout')
            plt.close(fig)
            has_next = self.next()


class TextBox:

    def __init__(self, x, y, string: str, va='top', ha='left', **kwargs):
        self.x = x
        self.y = y
        self.string = string
        fontdict = {'va': va, 'ha': ha}
        fontdict.update(kwargs)
        self.fontdict = fontdict

    def draw(self, ax, values: Optional[dict] = None):
        text = self.string.format(**values) if values else self.string
        ax.text(self.x, self.y, text, transform=ax.transAxes, **self.fontdict)
