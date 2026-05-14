def get_or_create_subfolder(parent, name):
    for folder in parent.Folders:
        if folder.Name.lower() == name.lower():
            return folder
    return parent.Folders.Add(name)


def ensure_subfolders(inbox, sent_folder, config):
    received_folders = {
        name: get_or_create_subfolder(inbox, name)
        for name in config["folders"]["received"]
    }
    sent_folders = {
        name: get_or_create_subfolder(sent_folder, name)
        for name in config["folders"]["sent"]
    }
    return received_folders, sent_folders
