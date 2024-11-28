project = "DEA Mosaic Builder"
project_copyright = "%Y, Joel Rhine"
author = "Joel Rhine"

html_theme = "furo"

html_static_path = ["_static"]
html_theme_options = {
    "sidebar_hide_name": True,
    "light_logo": "rwd-header-light.png",
    "dark_logo": "rwd-header-dark.png",
    "source_repository": "https://github.com/rhinejoel/dea-mosaic-builder",
    "source_branch": "main",
    "source_directory": "docs/source/",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/rhinejoel/dea-mosaic-builder",
            "html": "",
            "class": "fa-brands fa-solid fa-github fa-x",
        },
        {
            "name": "LinkedIn",
            "url": "https://www.linkedin.com/in/joel-rhine",
            "html": "",
            "class": "fa-brands fa-linkedin fa-x",
        },
        {
            "name": "Email",
            "url": "mailto:joelrhine7@gmail.com",
            "html": "",
            "class": "fa-solid fa-envelope fa-x",
        },
    ],
}
html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css",
]
