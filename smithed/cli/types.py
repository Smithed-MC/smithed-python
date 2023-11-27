"""Contains types for easy interaction with Smithed web API

"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum, auto
import typing

PackCategory = Enum('PackCategory', ['Extensive', 'Lightweight', 'QoL', 'Vanilla+', 'Tech', 'Magic', 'Library', 'Exploration', 'World Overhaul', 'No Resource Pack'])
MinecraftVersion = Enum('MinecraftVersion', ['1.17', '1.17.1', '1.18', '1.18.1', '1.18.2', '1.19', '1.19.4', '1.20', '1.20.1'])
SortOption = Enum('SortOptions', ['trending', 'downloads', 'alphabetically', 'newest'])

@dataclass
class PackReference:
    """A type which defines a pack reference.

    :param pack_id: the id of the datapack
    :type pack_id: str

    :param version: the version of the datapack
    :type version: str
    """
    id           : str
    version      : str 

@dataclass
class PackDownload:
    """A type which represents subpacks a pack downloads

    :param datapack: the datapack to be downloaded
    :type datapack: Optional str

    :param resourcepack: the resourcepack to be downloaded
    :type resourcepack: Optional str
    """
    datapack     : Optional[str]
    resourcepack : Optional[str]

@dataclass
class PackVersion:
    """
    A type which represents a datapack version

    :param name: Name of the pack
    :type name: str

    :param downloads: What the pack will download
    :type downloads: PackDownload

    :param supports: The minecraft versions the pack supports.
    :type supports: MinecraftVersion

    :param dependencies: The dependencies of the datapack.
    :type dependencies: PackReference
    """
    name         : str
    downloads    : PackDownload
    supports     : list[MinecraftVersion]
    dependencies : list[PackReference]

@dataclass
class PackDisplay:
    """A type representing datapack display data

    :param name: The display name of the datapack.
    :type name: str

    :param description: The description of the datapack.
    :type description: str

    :param icon: The link of the datapack icon.
    :type icon: str

    :param hidden: Is this pack hidden or not.
    :type hidden: bool

    :param webPage: Link to the webpage of the datapack.
    :type webPage: Optional str
    """
    name         : str
    description  : str 
    icon         : str
    hidden       : bool 
    webPage      : Optional[str]

@dataclass
class PackData:
    """A type representing whole pack data
    
    :param pack_id: Id of the datapack.
    :type pack_id: str

    :param display: Display data of the pack.
    :type display: PackDisplay

    :param versions: The versions this datapack has released
    :type versions: List of PackVersion's

    :param categories: The categories this datapack is in.
    :type categories: List of packCategory's
    """
    id           : str
    display      : PackDisplay
    versions     : list[PackVersion]
    categories   : list[PackCategory]

@dataclass
class DownloadCount:
    """A type to represent download metrics.

    :param total: The total downloads of the datapack.
    :type total: int

    :param today: The downloads of the pack today.
    :type today: int
    """
    total        : int
    today        : int

@dataclass
class PackStats:
    """A type to represent the statistics of a datapack.

    :param updated: The amount of times updated? TODO: Come back and change this
    :type updated: int

    :param added: The bundles this is in? TODO: Come back and correct this
    :type added: int

    :param downloads: The downloads this pack has gotten.
    :type downloads: DownloadCount
    """
    updated      : Optional[int]
    added        : int
    downloads    : DownloadCount

@dataclass
class PackMetadata:
    """A type to represent pack metadata

    :param doc_id: The pack ID - random garbage edition
    :type doc_id: str

    :param raw_id: The pack ID - plaintext
    :type raw_id: str

    :param stats: Statistics of the datapack
    :type stats: PackStats

    :param owner: Owner of the datapack
    :type owner: str

    :param contributors: Contributors of the datapack 
    :type contributors: List of str's
    """
    docId        : str
    rawId        : str
    stats        : PackStats
    owner        : str
    contributors : list[str]

@dataclass
class PackBundle:
    """A type representing a pack bundle.

    :param owner: The owner of the bundle.
    :type owner: str

    :param name: The name of the bundle
    :type name: str

    :param version: The minecraft version this bundle is made for.
    :type version: MinecraftVersion

    :param packs: The packs within this bundle.
    :type packs: List of PackReference's

    :param is_public: Is this bundle within public view.
    :type is_public: bool

    :param uid: The uid of the pack? (Not sure on this one)
    :type uid: Optional str
    """
    owner        : str
    name         : str
    version      : MinecraftVersion
    packs        : list[PackReference]
    public       : bool
    uid          : Optional[str] 

@dataclass
class UserData:
    """ A type to represent a user.

    :param displayName: The display name of the user.
    :type displayName: str

    :param cleanName: The clean name of the user.
    :type cleanName: str

    :param creationTime: The time the account was created.
    :type creationTime: int

    :param uid: The uid of the user.
    :type uid: str

    :param pfp: The link to the user PFP.
    :type pfp: Optional str
    """
    displayName  : str
    cleanName    : str
    creationTime : int
    uid          : str
    pfp          : Optional[str]
