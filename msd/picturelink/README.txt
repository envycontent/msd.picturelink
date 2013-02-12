Introduction
============

The PictureLink content type is not really meant to be used "in the raw". For that reason it isn't globally addable (i.e. won't show up in content menus) and doesn't have a skins folder.

The key features of the PictureLink content type are:

1. A link
2. An image and optional caption
3. A description that is rich text (i.e. includes HTML)

Special mention needs to be made concerning the rich text description. Putting HTML into a description field has the capacity to break certain things (such as the navigation tree, where the description appears when you hover over an item).

There's some coding behind the scenes which should ensure that only plain text gets passed to the description in the catalog and anywhere that the accessor context/Description or here/Description is used.

If you use getHTMLDescription however, you'll get the rich text version.

One thing we need to do though is discourage people from writing too much in the description. I might be able to do this with a validator, but we should also control the size of the Kupu widget, which I think needs to be done in the CSS - probably on a case-by-case basis.


