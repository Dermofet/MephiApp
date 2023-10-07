# import argostranslate.package
# import argostranslate.translate

# import config

# # Download and install Argos Translate package
# argostranslate.package.update_package_index()
# available_packages = argostranslate.package.get_available_packages()
# for lang in config.config.FOREIGN_LANGS:
#     package_to_install = next(
#         filter(
#             lambda x: x.from_code == lang[0] and x.to_code == lang[1], available_packages
#         )
#     )
#     path = package_to_install.download()
#     print(f"Path: {path}")
#     argostranslate.package.install_from_path(path)
