import neovim
import os
import re


@neovim.plugin
class Main(object):
    def __init__(self, vim):
        self.vim = vim

    @classmethod
    def debug(cls, nvim_listen_address):
        vim = neovim.attach("socket", path=nvim_listen_address)
        return cls(vim)

    @neovim.command("ZettelBackLinksAsync", nargs="*", range="")
    def zettelBackLinksAsync(self, args, range):
        file_name = self.getCurrentFileName()
        link_regex = self.getLinkRegex(file_name)

        files_with_links = list()
        wiki_vars = self.vim.eval("g:vimwiki_list")
        for w in wiki_vars:
            path = w["path"]
            ext = w["ext"]

            for root, _, files in os.walk(path):
                for f in files:
                    if ext in f:
                        name, _ = os.path.splitext(f)
                        title = name
                        with open(os.path.join(root, f)) as current_file:
                            file_content = current_file.read().splitlines()
                            for line in file_content:
                                if "title:" in line:
                                    title = line.replace("title:", "").strip()

                                links_found = re.findall(link_regex, line)
                                if len(links_found) > 0:
                                    files_with_links.append(
                                        dict(
                                            title=title,
                                            current_file=os.path.splitext(f)[0],
                                        )
                                    )
                                    break

        if self.checkIfFileStillOpen(file_name):
            self.writeNewBackLinks(files_with_links)

    def getCurrentFileName(self):
        name, _ = os.path.splitext(os.path.basename(self.vim.current.buffer.name))
        return name

    def getLinkRegex(self, filename):
        return "\[.*\]\(" + filename + "\)"

    def checkIfLinkExists(self):
        pass

    def checkIfFileStillOpen(self, original_filename):
        return self.getCurrentFileName() == original_filename

    def writeNewBackLinks(self, files_with_links):

        backlinks_list = list()
        backlinks_list.append("# Backlinks")
        backlinks_list.append("")

        for f in files_with_links:
            backlinks_list.append("- [" + f["title"] + "](" + f["current_file"] + ")")

        try:
            backlinks_index = self.vim.current.buffer[:].index("# Backlinks")

            if self.vim.current.buffer[backlinks_index:] == backlinks_list:
                pass
            else:
                del self.vim.current.buffer[backlinks_index:]
                self.vim.current.buffer.append(backlinks_list)

        except:
            self.vim.current.buffer.append(backlinks_list)
