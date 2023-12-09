import ubinascii as binascii
import uhashlib as hashlib
import ujson as json
import uos as os
import urequests

CONFIG_FILE = '/.github.json'


class Github:
  def __init__(self, user: str, repo: str, ref: str, token: str | None = None):
    self.tree_url = f'https://api.github.com/repos/{user}/{repo}/git/trees/{ref}?recursive=1'
    self.raw_url = f'https://raw.githubusercontent.com/{user}/{repo}/{ref}'
    self.headers = {
        'User-Agent': 'ugit-north101',
    }
    if token:
      self.headers['Authorization'] = f'Bearer {token}'

  @staticmethod
  def from_config(path=CONFIG_FILE):
    with open(path, 'r') as f:
      data = json.load(f)
      f.close()

    return Github(
      user=data['user'],
      repo=data['repo'],
      ref=data['ref'],
      token=data.get('token'),
    )

  @staticmethod
  def save_config(user: str, repo: str, ref: str, token: str | None = None, path=CONFIG_FILE):
    with open(path, 'w') as f:
      json.dump({
        user: user,
        repo: repo,
        ref: ref,
        token: token,
      }, f)
      f.close()

  def pull_file(self, file_path: str, git_path: str | None = None):
    try:
      r = urequests.get(f'{self.raw_url}{git_path or file_path}', headers=self.headers)
      self.mkdir(file_path)
      with open(file_path, 'wb') as f:
        f.write(r.content)
        f.close()
    except:
      self.print(f'Failed to download: {file_path}')

  def pull(self, git_root: str | None = None, ignore: list[str] | None = None, ignore_dot_files=True):
    self.print(f'Pulling repo: {self.raw_url}')

    git_root = self.normalize_path(git_root if git_root else '', is_dir=True)
    ignore = [
        self.normalize_path(path)
        for path in ignore
    ] if ignore else []
    # Ignore this file
    ignore.append(__file__)

    device_files = list(self.list_device_files('/'))
    for git_path, git_hash in self.list_git_files():
      if not git_path.startswith(git_root):
        continue

      path = git_path[len(git_root)-1:]
      if self.is_ignored(ignore, path, ignore_dot_files):
        self.print(f'{"Ignored":<9} {path}')
        continue

      file_hash = self.hash_file(path) if path in device_files else None
      if file_hash != git_hash:
        self.pull_file(path, git_path)
        if file_hash:
          self.print(f'{"Replaced":<9} {path}')
        else:
          self.print(f'{"Created":<9} {path}')
      else:
        self.print(f'{"Unchanged":<9} {path}')

      # Don't delete device_files from github repo
      if path in device_files:
        device_files.remove(path)

    # Delete any remaining device_files
    for path in device_files:
      if not self.is_ignored(ignore, path, ignore_dot_files):
        self.print(f'{"Removed":<9} {path}')
        os.remove(path)
        self.rmdir(path)

  def get_git_tree(self):
    data = urequests.get(self.tree_url, headers=self.headers).json()
    if 'tree' not in data:
      raise Exception(f'ugit: {self.tree_url} not found')

    return data['tree']

  def list_git_files(self):
    for item in self.get_git_tree():
      type = item['type']
      path = item['path']
      sha = item['sha'].encode('utf-8')
      if type == 'blob':
        yield self.normalize_path(path, is_dir=False), sha

  def list_device_files(self, path: str):
    for name, type, *_ in os.ilistdir(path):
      sub_path = f'{self.normalize_path(path, is_dir=True)}{name}'
      if type & 0x4000:
        yield from self.list_device_files(sub_path)
      else:
        yield sub_path

  def hash_file(self, path: str):
    try:
      with open(path, 'rb') as f:
        data = f.read()
        f.close()

      sha1obj = hashlib.sha1()
      sha1obj.update(f'blob {len(data)}\0')
      sha1obj.update(data)
      hash = sha1obj.digest()
      return binascii.hexlify(hash)
    except:
      return None

  def is_ignored(self, ignore: list[str], path: str, ignore_dot_files: bool):
    if path in ignore:
      return True

    for ignore_path in ignore:
      if ignore_path.endswith('/') and path.startswith(ignore_path):
        return True

    if ignore_dot_files:
      for part in path.split('/'):
        if part.startswith('.'):
          return True

    return False

  def print(self, *args, **kwargs):
    print('ugit:', *args, **kwargs)

  def split_path(self, path):
    return [
        part
        for part in path.split('/')
        if part
    ]

  def join_path(self, path: list[str], is_dir=False):
    return f'/{"/".join(path)}{"/" if path and is_dir else ""}'

  def normalize_path(self, path: str, is_dir: bool | None = None):
    if is_dir is None:
      is_dir = path.endswith('/')

    return self.join_path(self.split_path(path), is_dir)

  def mkdir(self, path: str):
    parts = self.split_path(path)[:-1]
    for i in range(len(parts)):
      try:
        sub_dir = self.join_path(parts[:i+1])
        os.mkdir(sub_dir)
        self.print(f'{"Created":<9} {sub_dir}')
      except OSError:
        pass

  def rmdir(self, path: str):
    parts = self.split_path(path)[:-1]
    for i in reversed(range(len(parts))):
      try:
        sub_dir = self.join_path(parts[:i+1])
        os.rmdir(sub_dir)
        self.print(f'{"Removed":<9} {sub_dir}')
      except OSError:
        # Dir not empty
        return


def update(user='North101', repo='ugit', ref='master', file_path=__file__, git_path='/ugit.py', token: str | None = None):
  return Github(
    user=user,
    repo=repo,
    ref=ref,
    token=token,
  ).pull_file(
    file_path=file_path,
    git_path=git_path,
  )
